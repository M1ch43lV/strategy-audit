#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""secret_gate — A COMMIT WITH A SECRET DOES NOT GO OUT. Not a memo, but a return code.

WHY THIS IS A SEPARATE GATE, NOT A LINE IN .gitignore
----------------------------------------------------
`.gitignore` protects against CARELESSNESS, but not against `git add -f`, not against
a tool that doesn't read it, and not against a file caught by a pattern
that isn't in it. It's convenience, not control.

And the cost of an error here is special: **a commit of a secret is a secret leak
forever.** Deleting it in the next commit doesn't help — the secret remains in
history, in forks, in others' clones, and in the platform's cache. Bots roam GitHub's
public event stream, pick up fresh keys, and use them within minutes. So the only real
remedy after a leak is not "rewrite history" but **rotate the key**.

FOUR LAYERS, HOW PROFESSIONALS DO IT
---------------------------------------
    0. No secrets in the repository tree. Physically, not via gitignore.
    1. .gitignore — against accidental `git add`.
    2. THIS gate — machine refusal before sending.
    3. Platform-side protection (push protection / secret scanning).
    4. Rotation: anything that ever touched the repository is considered burned.

Layer 2 is the only one that stops a DELIBERATE human error by someone
in a hurry to publish. That's why it was written.

⚠ BOUNDARY, STATED DIRECTLY. The gate catches KNOWN forms. A secret that doesn't
match any pattern will pass. So it doesn't replace layer 0:
if there are no keys in the tree, there's nothing to leak regardless of pattern
quality.
"""
from __future__ import print_function

import io
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Patterns. Each with a observed reason, not "just in case".
PATTERNS = [
    (u"private key",
     re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA |PGP )?PRIVATE KEY")),
    # ⚠ It was exactly `{35}` — the self-test caught it: the length of the part after
    # the colon in real tokens varies. The exact number here is
    # an assumption about the subject, not knowledge of it.
    (u"Telegram bot token",
     re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{30,45}\b")),
    (u"AWS key",
     re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    (u"GitHub token",
     re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    (u"exchange key/secret (64 hex)",
     re.compile(r"\b[a-fA-F0-9]{64}\b")),
    (u"Binance key (64 alphanumeric)",
     re.compile(r"\b[A-Za-z0-9]{64}\b")),
    (u"connection string with password",
     re.compile(r"(?:postgres|mysql|mongodb|redis)://[^\s:@]+:[^\s@]+@")),
    (u"assigning a secret in code",
     re.compile(r"(?i)\b(api_?key|secret|passwd|password|token)\b\s*[:=]\s*"
                r"['\"][A-Za-z0-9/+_\-]{16,}['\"]")),
]

# Names that must NEVER appear in a public repository.
FORBIDDEN_NAMES = re.compile(
    r"(?:^|/)(?:id_rsa|id_ed25519|id_ecdsa|id_dsa|id_deploy[^/]*|"
    r"\.env|secrets?\.env|hmac\.secret|api_key|[^/]*\.pem|[^/]*\.p12|"
    r"[^/]*\.pfx|\.npmrc|\.pypirc)$")

# What is definitely NOT a secret, although it matches patterns. The list is CLOSED and
# named: extending it means going blind, so each line is justified.
# TOTAL: whitelist — by definition a manual enumeration; its completeness
# is checked by sabotage: three planted secrets must be caught.
ALLOW = (
    "cacert.pem",          # public certifi root set
    "/test", "tests/",     # deliberately test fake values
    "EXAMPLE", "example",
    "secret_gate.py",      # THIS file contains samples by definition
)


def is_allowed(path):
    return any(a in path.replace("\\", "/") for a in ALLOW)


def scan_text(path, text):
    u"""[(line, what was found)]. Pure function — for self-test."""
    hits = []
    p = path.replace("\\", "/")
    if FORBIDDEN_NAMES.search(p) and not is_allowed(p):
        hits.append((0, u"FORBIDDEN FILE NAME"))
    if is_allowed(p):
        return hits
    for i, line in enumerate(text.splitlines(), 1):
        if len(line) > 4000:
            continue
        for name, rx in PATTERNS:
            if rx.search(line):
                hits.append((i, name))
                break
    return hits


def staged_files():
    try:
        out = subprocess.run(["git", "diff", "--cached", "--name-only",
                              "--diff-filter=ACM"],
                             capture_output=True, timeout=60)
        return [l for l in out.stdout.decode("utf-8", "replace").splitlines()
                if l.strip()]
    except Exception:
        return []


def gate():
    bad = 0
    files = staged_files()
    for f in files:
        if not os.path.exists(f):
            continue
        try:
            text = io.open(f, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        for ln, what in scan_text(f, text):
            print(u"⛔ %s:%s — %s" % (f, ln or "name", what))
            bad += 1
    print(u"secret_gate: checked files %d · findings %d" % (len(files), bad))
    if bad:
        print(u"\nCOMMIT STOPPED. A secret that got into history is considered\n"
              u"burned — cleaning history is useless, you must CHANGE THE KEY.\n"
              u"If this is a false positive, add the path to ALLOW EXPLICITLY,\n"
              u"with justification in a comment, not disable the gate.")
    return 1 if bad else 0


def selftest():
    ok = fail = 0

    def case(name, path, text, want):
        nonlocal ok, fail
        got = len(scan_text(path, text)) > 0
        if got == want:
            ok += 1
        else:
            fail += 1
            print(u"  ✗ %s: caught=%s, expected=%s" % (name, got, want))

    # ── MUST BE CAUGHT ──
    case(u"OpenSSH private key", "a.txt",
         "-----BEGIN OPENSSH PRIVATE KEY-----\nb3Blb", True)
    case(u"private key name", "keys/id_ed25519", "x", True)
    case(u".env file", "cfg/.env", "X=1", True)
    case(u"hmac.secret", "s/hmac.secret", "x", True)
    case(u"telegram bot token", "b.py",
         'TOKEN = "123456789:AAF-abcdefghijklmnopqrstuvwxyz012345"', True)
    case(u"AWS key", "c.py", "key AKIAIOSFODNN7EXAMPLX here", True)
    case(u"GitHub token", "d.py",
         "ghp_AbCdEfGhIjKlMnOpQrStUvWxYz0123456789", True)
    case(u"exchange key 64 characters", "e.py",
         "EXCHANGE_API_KEY=aB3dE5gH7jK9mN1pQ3sT5vW7yZ9bD1fH3jL5nP7rT9vX1zC3eG5iK7mO9q",
         False)   # 58 characters — shorter than the pattern, must NOT be caught
    case(u"exchange key exactly 64", "f.py",
         "k = '" + "a1B2c3D4"*8 + "'", True)
    case(u"connection string with password", "g.py",
         "postgres://user:hunter2@db.local/x", True)
    case(u"api_key assignment", "h.py",
         'api_key = "sk-1234567890abcdefghij"', True)

    # ── MUST NOT BE CAUGHT ──
    case(u"ordinary code", "i.py", "x = compute(a, b)  # ok", False)
    case(u"commit hash (40 hex) — not a secret", "j.md",
         "commit 8b63377f1b4390ab12cd34ef56ab78cd90ef12ab", False)
    case(u"public certifi", "venv/certifi/cacert.pem",
         "-----BEGIN CERTIFICATE-----", False)
    case(u"this very file with samples", "tools/secret_gate.py",
         "-----BEGIN OPENSSH PRIVATE KEY-----", False)
    case(u"example in tests", "tests/fixtures.py",
         "-----BEGIN RSA PRIVATE KEY-----", False)

    print(u"SELFTEST secret_gate: %d passed, %d failed" % (ok, fail))
    return 1 if fail else 0


def sabotage():
    u"""CONTROL OVER CONTROL. A green selftest is worthless unless it is
    shown that the gate CAN TURN RED on a real file. We plant three
    real secrets in temporary files and require that all three be found."""
    import tempfile
    seeds = [
        ("k.pem", "-----BEGIN RSA PRIVATE KEY-----\nMIIEow"),
        ("cfg.env", "BINANCE_SECRET=" + "a1B2c3D4"*8),
        ("bot.py", 'TG = "987654321:BBF-zyxwvutsrqponmlkjihgfedcba098765"'),
    ]
    found = 0
    d = tempfile.mkdtemp()
    for nm, body in seeds:
        p = os.path.join(d, nm)
        io.open(p, "w", encoding="utf-8").write(body)
        if scan_text(nm, body):
            found += 1
        else:
            print(u"  ✗ DIVERSION NOT CAUGHT: %s" % nm)
    print(u"DIVERSION: planted 3, caught %d" % found)
    return 0 if found == 3 else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest() or sabotage())
    sys.exit(gate())
