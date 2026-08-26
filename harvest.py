# -*- coding: utf-8 -*-
u"""harvest — fetch ONLY strategy files, without cloning the repository.

RATIONALE. I cut four repositories by size (>60 MB) and recorded this as a
stated limit. Verification showed the limit was chosen by the WRONG
criterion: they are heavy with BACKTEST RESULTS and data, not strategies.
MoniGoMani — 271 MB and 21 .py files. GeneTrader — 226 MB and 49.

Repository size says nothing about the number of strategies. The criterion is replaced:
we get the tree via API, download only .py files, keep those that have
IStrategy. The size limit disappears along with the caveat in the report.

⚠ Nothing is executed: files are placed on disk and parsed with AST by the same
find_strategies as the rest of the corpus.
"""
from __future__ import print_function

import io
import json
import os
import subprocess
import sys

_ROOT = os.environ.get("AUDIT_ROOT") or os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from harness import find_strategies

REPOS = os.path.join(_ROOT, "repos")
GH = "C:/tmp/tools/gh/bin/gh.exe"
MAX_FILE = 600000


def gh_json(path):
    r = subprocess.run([GH, "api", path], capture_output=True, timeout=180)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout.decode("utf-8", "replace"))
    except Exception:
        return None


def raw(full, branch, path):
    r = subprocess.run([GH, "api",
                        "repos/%s/contents/%s?ref=%s" % (full, path, branch),
                        "-H", "Accept: application/vnd.github.raw"],
                       capture_output=True, timeout=180)
    return r.stdout if r.returncode == 0 else None


def harvest(full):
    d = full.replace("/", "_", 1)
    out_dir = os.path.join(REPOS, d)
    meta = gh_json("repos/" + full)
    if not meta:
        return (full, 0, 0, u"repository unavailable")
    br = meta.get("default_branch") or "main"
    tree = gh_json("repos/%s/git/trees/%s?recursive=1" % (full, br))
    if not tree or "tree" not in tree:
        return (full, 0, 0, u"tree not fetched")
    pys = [t for t in tree["tree"]
           if t.get("type") == "blob" and t["path"].endswith(".py")
           and (t.get("size") or 0) < MAX_FILE]
    got = 0
    for t in pys:
        body = raw(full, br, t["path"])
        if not body or b"IStrategy" not in body:
            continue
        dst = os.path.join(out_dir, t["path"].replace("/", os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as fh:
            fh.write(body)
        got += 1
    names = {n for _f, n in find_strategies(out_dir)} if os.path.isdir(out_dir) else set()
    return (full, got, len(names), u"")


def main():
    targets = sys.argv[1:]
    if not targets:
        print(u"specify repositories separated by spaces")
        return 2
    base = set()
    for x in sorted(os.listdir(REPOS)):
        p = os.path.join(REPOS, x)
        if os.path.isdir(p):
            base |= {n for _f, n in find_strategies(p)}
    print(u"unique classes before fetch: %d" % len(base), flush=True)
    grand = set(base)
    for full in targets:
        name, got, cls, err = harvest(full)
        if err:
            print(u"  ✗ %-46s %s" % (name, err), flush=True)
            continue
        p = os.path.join(REPOS, full.replace("/", "_", 1))
        names = {n for _f, n in find_strategies(p)}
        new = names - grand
        grand |= names
        print(u"  %-46s files %3d · classes %3d · NEW %3d"
              % (name, got, len(names), len(new)), flush=True)
    print()
    print(u"unique classes now: %d (increase %d)"
          % (len(grand), len(grand) - len(base)))


if __name__ == "__main__":
    sys.exit(main())
