# -*- coding: utf-8 -*-
"""Repos outside the 53 this corpus already knows about (`evidence/corpus_sources.json`),
checked for `IStrategy` classes not already present under any name.

WHERE THE CANDIDATE LIST COMES FROM. GitHub's `topic:freqtrade-strategies`
search (31 repos total) minus the 53 already-known ones, plus a handful named
in an outside conversation about this audit and worth checking on their own
merits regardless of where the name came from. This is a scan of specific,
named repos - not a general web crawl - because the topic search is itself
already narrow (31 hits) and a broader GitHub code search for
`"populate_indicators" "IStrategy"` returns thousands of forks and copies
with no signal beyond what a human already filtered for here.

NAME MATCH IS ONLY THE INTAKE CHECK. A name already in `STRATEGY_STATUS.csv`
(case-insensitive) is treated as already known here because it avoids a remote
download-and-parse of every candidate against the full local corpus.  A
`NEW`-flagged class is not thereby a distinct trading implementation: after
canonicalization, `evidence.semantic_duplicates` performs the local AST and
full-trade-hash comparison.  The two tools answer different questions and
neither silently excludes a strategy.
"""
from __future__ import annotations

import argparse
import base64
import csv
import io
import json
import os
import re
import subprocess


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS = os.path.join(ROOT, "STRATEGY_STATUS.csv")
OUTPUT_JSON = os.path.join(ROOT, "evidence/NEW_REPO_CANDIDATES.json")
OUTPUT_MD = os.path.join(ROOT, "evidence/NEW_REPO_CANDIDATES.md")
CLASS_RE = re.compile(r"^class\s+(\w+)\s*\(([^)]*)\)", re.M)

# Checked 2026-09-05. Add to this list rather than replacing it, so a repo
# already found to add nothing (paulcpk, joaorafaelm) is not re-fetched by
# accident next time.
#
# 2026-09-06 additions: named search for futures/short-specialised strategies
# (`can_short = True`, "short strategy", "long short"), since 855 of 919
# corpus rows are long-only. `LazyPigPig/freqtrade-short-strategy` is an
# empty repo (size 0, README only) and `LazyPigPig/freqtrade-grid` is a
# freqtrade framework fork, not a strategy collection - both kept in this
# list so neither is re-fetched believing it might hold something.
CANDIDATES = [
    "hippocritical/delist_scraper",
    "Netanelshoshan/freqAI-LSTM",
    "AlexCryptoKing/freqailstm",
    "djienne/YOUTUBE_STRATEGIES_FREQTRADE",
    "mmartel86/freqtrade-setup",
    "thinkong/freqtradestrategies",
    "kemplail/freqtrade-stuff",
    "hamidreza07/freqai-strategy",
    "webclinic017/strategies-freqtrade-",
    "LazyPigPig/freqtrade-short-strategy",
    "LazyPigPig/freqtrade-grid",
    "paulcpk/freqtrade-strategies-that-work",
    "brookmiles/freqtrade-stuff",
    "titouannwtt/freqtrade-ultimate",
    "titouannwtt/freqtrade-france-strategies-kac-index",
    "titouannwtt/freqtrade-france-strategies_simple_vwap",
    "miwtoo/ft-action-zone",
    "keithorange/FreqTrade_Helpers",
    "DonaldSimpson/remora-backtests",
    "freqstart/freqstart",
    "kiploks/kiploks-freqtrade",
    "amcalabretta/botbase",
    "Ph3nol/FT-Trading-Bot",
    "meesvw/freqtrade-egg",
    "mcDucksProject/mcDucksBroker",
    "shadowp2810/technical_indicators_cryptos",
    "joaorafaelm/freqtrade-heroku",
    "freqsignals/freqtrade-strategies",
    "Lijunnan0113/Lijunnan0113-Lijunnan_Freqtrade_Strategy",
]


def known_names():
    with io.open(STATUS, encoding="utf-8-sig", newline="") as handle:
        return {row["strategy_id"].lower() for row in csv.DictReader(handle)}


def gh(args):
    out = subprocess.run(["gh"] + args, capture_output=True, timeout=90)
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout.decode("utf-8", "replace"))
    except ValueError:
        return None


def tree(repo):
    meta = gh(["api", "repos/%s" % repo])
    if not meta:
        return None, []
    branch = meta.get("default_branch", "main")
    data = gh(["api", "repos/%s/git/trees/%s?recursive=1" % (repo, branch)])
    if not data:
        return meta, []
    return meta, [item["path"] for item in data.get("tree", [])
                 if item["type"] == "blob" and item["path"].endswith(".py")]


def fetch(repo, path):
    data = gh(["api", "repos/%s/contents/%s" % (repo, path)])
    if not data or "content" not in data:
        return ""
    try:
        return base64.b64decode(data["content"]).decode("utf-8", "replace")
    except Exception:
        return ""


def scan(repo, known):
    meta, files = tree(repo)
    if meta is None:
        return {"repo": repo, "status": "not_found"}
    found = []
    for path in files:
        if "/test" in path or "backtest_results/" in path:
            continue
        text = fetch(repo, path)
        for match in CLASS_RE.finditer(text):
            name, bases = match.group(1), match.group(2)
            if "IStrategy" in bases:
                found.append({"class": name, "path": path,
                             "known": name.lower() in known})
    return {"repo": repo, "status": "ok", "pushed_at": meta.get("pushed_at"),
            "py_files": len(files), "classes": found}


def _report(rows):
    lines = [
        "# New repo candidates - unclaimed strategy names outside the corpus",
        "", "**Generated by `evidence/new_repo_candidates.py`.** See its docstring for",
        "where the candidate list comes from and why novelty is decided by",
        "class name, not content. A `new` class here is a name this corpus",
        "does not yet use - not a verdict that it is worth admitting; each",
        "still needs a human look for test fixtures, mixins, and templates",
        "before being queued as a wave.", "",
    ]
    for row in rows:
        if row["status"] != "ok":
            lines += ["## `%s` - %s" % (row["repo"], row["status"]), ""]
            continue
        classes = row["classes"]
        new = [c for c in classes if not c["known"]]
        lines += [
            "## `%s` - %d new, %d already known" % (
                row["repo"], len(new), len(classes) - len(new)),
            "", "Pushed %s, %d `.py` files, %d `IStrategy` classes found." % (
                row.get("pushed_at", "-"), row["py_files"], len(classes)), "",
        ]
        if new:
            lines += ["| Class | Path |", "|---|---|"]
            for c in new:
                lines.append("| `%s` | `%s` |" % (c["class"], c["path"]))
            lines.append("")
    return "\n".join(lines).encode("utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", action="append", default=[],
                        help="scan only these repos, not the full candidate list")
    args = parser.parse_args(argv)
    known = known_names()
    print("known strategy names: %d" % len(known))
    rows = []
    for repo in (args.repo or CANDIDATES):
        row = scan(repo, known)
        rows.append(row)
        if row["status"] != "ok":
            print("%-58s %s" % (repo, row["status"]))
            continue
        new = [c for c in row["classes"] if not c["known"]]
        print("%-58s pushed=%-22s classes=%-3d new=%d" % (
            repo, row.get("pushed_at"), len(row["classes"]), len(new)))
        for c in new:
            print("    NEW  %-32s %s" % (c["class"], c["path"]))
    if not args.repo:
        io.open(OUTPUT_JSON, "w", encoding="utf-8").write(
            json.dumps(rows, indent=2, ensure_ascii=False))
        io.open(OUTPUT_MD, "wb").write(_report(rows))
        print("\nwrote %s, %s" % (OUTPUT_JSON, OUTPUT_MD))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
