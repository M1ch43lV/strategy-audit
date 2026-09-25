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

WHAT ELSE GETS FETCHED, AND WHY (2026-09-09). An IStrategy file that imports a
sibling helper used to leave the corpus with the strategy but not the helper -
`Config.py`, `alpha/*.py`, `polymarket/*.py` and the like never contain the
literal `IStrategy`, so the filter above always discarded them, and the
strategy was unrunnable from the moment it landed on disk. Restoring these
by hand after the fact, one GitHub fetch at a time, is exactly what happened
for BBBHold/Hammer/KeltnerBounce/BinanceStream and six more rows in the same
session - discoverable in advance, from the same tree listing harvest()
already has. `dependency_closure()` below does the same thing at harvest
time: parse each kept file's own `import`/`from import` lines, and for every
name that is a real path in this repository's own tree (not a guess - it is
either found there or it is not fetched), pull it in and parse IT too, up to
`MAX_CLOSURE` files. This does not make every strategy runnable - a name
that resolves to a PyPI package rather than a repo path is correctly left
alone, and a genuinely absent file stays absent - but it means the audit's
own later repair passes start from what the repository actually publishes,
not from an arbitrary 50% of it.

README* at the repository root is fetched unconditionally too: never
executed, occasionally the only place a strategy's intended timeframe or
config is written down in prose (`EmaCrossStrategy`'s 4h came from exactly
this kind of file, one directory below, once by hand - see
`evidence/eligibility_timeframe_repair.py`'s MANUAL dict). Capped at
MAX_FILE like everything else here.

SECURITY BOUNDARY, STATED DIRECTLY. Every fetched file is content-scanned by
`tools/malware_gate.py` before it touches disk - a pattern gate, not a
sandbox, documented there. A file that matches is not written and is
reported; nothing here executes a byte of what it fetches, matching the
module docstring's original guarantee, now extended to the closure and the
READMEs as well.
"""
from __future__ import print_function

import datetime
import io
import json
import os
import re
import subprocess
import sys
import argparse

_ROOT = (os.environ.get("AUDIT_ROOT") or
         os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from tools.harness import find_strategies
from tools import label_intake, malware_gate, strategy_classification, strategy_status_page
from evidence import (execution_profiles, market_phase_hypothesis,
                      semantic_duplicates, strategy_status)

REPOS = os.path.join(_ROOT, "repos")
# Append-only, never rewritten to drop a row: once a duplicate's source file
# is gone, evidence.semantic_duplicates.build() can no longer even form the
# group that justified removing it (a group needs >= 2 still-existing
# members), so the live SEMANTIC_DUPLICATE_ADJUDICATION.json self-erases the
# decision the moment it is acted on. This file is the permanent record of
# what was removed and why - evidence.strategy_status's own selftest reads
# it precisely because the live file cannot answer the question anymore.
REMOVED_DUPLICATES_LOG = os.path.join(_ROOT, "evidence", "REMOVED_DUPLICATE_SOURCES.json")
# Resolved from PATH rather than a fixed install location, which was specific
# to one earlier machine and no longer exists on this one.
GH = __import__("shutil").which("gh") or "gh"
MAX_FILE = 600000
# A closure runs on one repository's own tree, already capped at MAX_FILE per
# file; this bounds the COUNT so a repository that imports something with an
# enormous fan-in (a `utils` package half the codebase touches) cannot turn
# one strategy into a full clone by another name.
MAX_CLOSURE = 40


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


# Windows forbids these in a path segment (POSIX allows all of them, so a
# repo tree fetched via the GitHub API - itself POSIX-path-shaped - can
# contain any of them). `hamidreza07/freqai-strategy` has a literal `*` in
# `startegy test/5/*ADXDM/`, which crashed `os.makedirs` here with WinError
# 123 partway through a ten-repo harvest, leaving three repos unfetched.
_WIN_ILLEGAL = re.compile(r'[<>:"|?*]')


def _win_safe_segment(segment):
    cleaned = _WIN_ILLEGAL.sub("_", segment)
    return cleaned.rstrip(" .") or "_"


# Top-level `import a.b.c` / `from a.b.c import X` - the module actually
# resolved is `a`, whatever depth the statement names. Deliberately only
# reads the two plain statement forms; a conditional or lazily-computed
# import (inside a function, behind `try/except ImportError`) is left alone
# rather than guessed at.
_IMPORT_LINE = re.compile(
    r"^\s*(?:from\s+([A-Za-z_][\w]*)(?:\.[\w]+)*\s+import\b"
    r"|import\s+([A-Za-z_][\w]*)(?:\.[\w]+)*\b)", re.M)


def imported_top_names(text):
    names = set()
    for m in _IMPORT_LINE.finditer(text):
        names.add(m.group(1) or m.group(2))
    return names


def _tree_index(tree):
    u"""(directory, name) -> every tree entry whose path starts with
    `directory/name` (`""` for the repo root).

    Two resolutions share this one index, because freqtrade's own
    `--strategy-path` makes both real: `import alpha` inside a file at the
    repo root means a root-level `alpha.py`/`alpha/`, exactly like
    `repair/local_modules.py`'s own corpus search already assumes one stage
    later, at repair time - `mlsys-io/PortfolioBench`'s `alpha`/`polymarket`
    are this shape. But `import NNPredictor_LSTM0` inside a file that lives
    in its OWN per-strategy directory (`hamidreza07/freqai-strategy`'s
    `startegy test/5/**NNPredict/`, one folder per strategy, each with its
    own `utils/`) means a file NEXT TO the importing one, not at the repo
    root - `--strategy-path` puts that directory on `sys.path`, not the
    repo root, so root-level resolution alone would never find it. Missing
    this cost a manual, one-file-at-a-time GitHub fetch for `NNPredict`
    before this function was extended to try it.
    """
    index = {}
    for t in tree:
        if t.get("type") != "blob":
            continue
        parts = t["path"].split("/")
        directory = "/".join(parts[:-1])
        top = parts[-1]
        top_name = top[:-3] if top.endswith(".py") else top
        index.setdefault((directory, top_name), []).append(t)
        # A deeper file (`utils/ClassifierKeras.py`) also has to be findable
        # by the name of the PACKAGE directory one level up (`utils`), not
        # only by its own filename - the import is `from utils import X` or
        # `import utils.ClassifierKeras`, never the file's own basename.
        if len(parts) >= 2:
            pkg_dir = "/".join(parts[:-2]) if len(parts) > 2 else ""
            index.setdefault((pkg_dir, parts[-2]), []).append(t)
    return index


def _closure_one(full, br, index, fetched, directory, names):
    u"""Fetch what `names` (imported inside `directory`) resolve to, and what
    THEIR imports in turn resolve to, up to MAX_CLOSURE new files for this
    one seed. `fetched` is shared and checked first, so a file already
    pulled in for an earlier seed is never re-fetched or re-counted against
    this seed's own budget.
    """
    queue = {(name, directory) for name in names}
    seen = set()
    budget = MAX_CLOSURE
    while queue and budget > 0:
        name, want_dir = queue.pop()
        if (name, want_dir) in seen:
            continue
        seen.add((name, want_dir))
        # Sibling of the importing file first - the more specific claim,
        # and the one a repo-root-only search would have missed entirely.
        # Falls back to the repo root, which is where a shared package
        # meant for every strategy actually lives.
        entries = index.get((want_dir, name)) or index.get(("", name))
        if not entries:
            continue    # stdlib or a pip package, not something to fetch
        for t in entries:
            # Only source: a name resolving to a package directory pulls in
            # every blob under it in the tree index, and a repository can
            # commit anything there - model checkpoints (`.pth`), data,
            # accidentally-committed `__pycache__`. None of that is a
            # dependency a strategy import can need.
            if not t["path"].endswith(".py") or (t.get("size") or 0) >= MAX_FILE:
                continue
            if t["path"] in fetched:
                continue
            if budget <= 0:
                break
            body = raw(full, br, t["path"])
            if not body:
                continue
            fetched[t["path"]] = body
            budget -= 1
            child_dir = "/".join(t["path"].split("/")[:-1])
            try:
                text = body.decode("utf-8", "replace")
                for child_name in imported_top_names(text):
                    queue.add((child_name, child_dir))
            except Exception:
                pass


def dependency_closure(full, br, tree, seeds):
    u"""Every additional .py file the seed set's own imports name and this
    repository's tree actually contains, transitively. `seeds` is
    [(path, text), ...] - the path matters, to resolve a sibling-directory
    import correctly. Returns {path: body_bytes}; the caller decides what
    survives the security scan.

    MAX_CLOSURE is a PER-SEED budget, not one shared across the whole
    repository: a repo with many strategies, each with its own modest
    `utils/` (this session's own `hamidreza07/freqai-strategy`, ~94 classes)
    exhausted a single repo-wide cap before reaching most of them - whichever
    strategies' names a Python `set()` happened to pop first won, in an
    order nothing controls. Giving every seed its own budget means a
    heavyweight strategy elsewhere in the same repository cannot starve a
    different one's three-file dependency.
    """
    index = _tree_index(tree)
    fetched = {}
    for path, text in seeds:
        directory = "/".join(path.split("/")[:-1])
        names = imported_top_names(text)
        _closure_one(full, br, index, fetched, directory, names)
    return fetched


def _write_scanned(dst, body, blocked):
    hits = malware_gate.scan_bytes(body)
    if hits:
        blocked.append((dst, hits))
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "wb") as fh:
        fh.write(body)
    return True


def harvest(full):
    d = full.replace("/", "_", 1)
    out_dir = os.path.join(REPOS, d)
    meta = gh_json("repos/" + full)
    if not meta:
        return (full, 0, 0, u"repository unavailable")
    br = meta.get("default_branch") or "main"
    tree_resp = gh_json("repos/%s/git/trees/%s?recursive=1" % (full, br))
    if not tree_resp or "tree" not in tree_resp:
        return (full, 0, 0, u"tree not fetched")
    tree = tree_resp["tree"]
    pys = [t for t in tree
           if t.get("type") == "blob" and t["path"].endswith(".py")
           and (t.get("size") or 0) < MAX_FILE]
    readmes = [t for t in tree
              if t.get("type") == "blob"
              and os.path.basename(t["path"]).lower().startswith("readme")
              and (t.get("size") or 0) < MAX_FILE]

    got = 0
    blocked = []
    seeds = []
    for t in pys:
        # `Config.py` (any case) is kept unconditionally, without the
        # IStrategy check: it never contains that literal itself, only
        # values a sibling strategy reads (minimal_roi, stoploss,
        # timeframe, ...). Filtering by content instead of by name left it
        # unharvested every time - BBBHold, Hammer, KeltnerBounce and four
        # more rows in the same wave all failed on exactly this, restored by
        # hand afterwards rather than being on disk to begin with.
        is_config = os.path.basename(t["path"]).lower() == "config.py"
        body = raw(full, br, t["path"])
        if not body:
            continue
        if not is_config and b"IStrategy" not in body:
            continue
        safe_path = os.sep.join(_win_safe_segment(part)
                                for part in t["path"].split("/"))
        dst = os.path.join(out_dir, safe_path)
        if _write_scanned(dst, body, blocked):
            got += 1
            seeds.append((t["path"], body.decode("utf-8", "replace")))

    for t in readmes:
        body = raw(full, br, t["path"])
        if not body:
            continue
        safe_path = os.sep.join(_win_safe_segment(part)
                                for part in t["path"].split("/"))
        dst = os.path.join(out_dir, safe_path)
        # READMEs are prose, never executed - the scan still runs (a
        # payload pasted into a README as a "usage example" is exactly the
        # kind of thing a copy-pasting reader would run by hand), but a hit
        # here is not the same alarm as one in a file freqtrade will import.
        _write_scanned(dst, body, blocked)

    closure = dependency_closure(full, br, tree, seeds)
    for path, body in closure.items():
        safe_path = os.sep.join(_win_safe_segment(part)
                                for part in path.split("/"))
        dst = os.path.join(out_dir, safe_path)
        if _write_scanned(dst, body, blocked):
            got += 1

    names = {n for _f, n in find_strategies(out_dir)} if os.path.isdir(out_dir) else set()
    err = u""
    if blocked:
        err = (u"%d file(s) blocked by malware_gate (written: %d): %s"
              % (len(blocked), got,
                 "; ".join("%s (%s)" % (p, ", ".join(n for _l, n in h))
                          for p, h in blocked[:5])))
    return (full, got, len(names), err)


def _already_checked():
    """Every strategy_id any check has a record for, whatever it says.

    A failed trial run counts: it is still a look at the strategy, and the
    row it produced is what a later repair is measured against.
    """
    checked = set()
    for path, key in ((os.path.join(_ROOT, "evidence", "PROFILE_SMOKE.json"), "results"),
                      (os.path.join(_ROOT, "evidence", "PROFILE_BIAS.json"), "results")):
        if not os.path.exists(path):
            continue
        with io.open(path, encoding="utf-8") as handle:
            checked |= set(json.load(handle).get(key, {}))
    manifest = os.path.join(_ROOT, "results", "regime", "full_backtest_manifest.json")
    if os.path.exists(manifest):
        with io.open(manifest, encoding="utf-8") as handle:
            data = json.load(handle)
        entries = data.get("runs", data) if isinstance(data, dict) else data
        if isinstance(entries, dict):
            checked |= set(entries)
        else:
            checked |= {row.get("strategy_id") for row in entries if isinstance(row, dict)}
    return {name for name in checked if name}


def _deletable_ids(fresh_repos, profiles):
    """The owner's rule of 2026-09-16, as a set of strategy_ids.

    Only a strategy this harvest just downloaded, and that no check has yet
    looked at, may lose its source file to a duplicate finding. Anything
    already measured is excluded and left on disk: other strategies import
    from these files, and an exclusion is a statement about a strategy, not
    a licence to delete source. With no fresh repos - `refresh_intake_evidence`
    called on its own, to regenerate evidence without downloading - the set
    is empty and nothing is deleted at all.
    """
    if not fresh_repos:
        return set()
    prefixes = tuple("repos/%s/" % repo for repo in sorted(fresh_repos))
    checked = _already_checked()
    return {strategy_id for strategy_id, row in profiles.items()
            if row["original_file"].startswith(prefixes) and strategy_id not in checked}


def remove_semantic_duplicates(fresh_repos=None):
    """Delete the source file of a duplicate this harvest just downloaded and
    no check has looked at yet - owner's rule, 2026-09-16 (REGISTER.md Phase
    18): deletion belongs at intake, so a copy never enters the corpus in the
    first place, and nowhere else. A strategy that has already been measured
    is excluded on the duplicate finding and keeps its file, because other
    strategies import from these files and because the finding is a statement
    about a strategy rather than a licence to remove source.

    `fresh_repos` is the set of repo directory names (`owner_repo`, as they
    appear under `repos/`) this run fetched. Without it nothing is deletable,
    which is what `refresh_intake_evidence()` wants when it is called on its
    own to regenerate evidence.

    The first version of this function deleted every adjudicated duplicate
    regardless of age, which removed 54 files that the rule above protects:
    34 where the kept representative was a differently-named file in the
    same author's own repo, and the 20-file `Anomaly_*` family, deleted out
    of its own source repo while a copy in another repo's scratch directory
    became the representative. All 54 were re-fetched.

    Only `evidence.execution_profiles.discover()`'s own filesystem scan
    defines the corpus, so deleting the file IS the removal - nothing else
    needs editing, only regenerating, which the caller does next. Idempotent:
    a strategy already removed is absent from the manifest, so
    `duplicate_source_files()` skips it rather than re-deleting or erroring.
    """
    data = semantic_duplicates.build()
    decisions = semantic_duplicates.adjudicate(data)
    profiles = {row["strategy_id"]: row
                for row in semantic_duplicates._read_csv(semantic_duplicates.PROFILES)}
    deletable = _deletable_ids(fresh_repos, profiles)
    resolved = semantic_duplicates.duplicate_source_files(
        decisions, profiles=profiles, restrict_to=deletable)
    removed = []
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for row in resolved:
        path = os.path.join(_ROOT, row["original_file"].replace("/", os.sep))
        if not os.path.exists(path):
            continue
        os.remove(path)
        removed.append(dict(row, removed_at=now))
        print(u"  removed duplicate: %-34s (of %s, %s)"
              % (row["strategy_id"], row["canonical_representative"], row["evidence_rule"]),
              flush=True)
    if removed:
        log = {"schema_version": 1, "removed": []}
        if os.path.exists(REMOVED_DUPLICATES_LOG):
            with io.open(REMOVED_DUPLICATES_LOG, encoding="utf-8") as handle:
                log = json.load(handle)
        already = {entry["strategy_id"] for entry in log["removed"]}
        log["removed"].extend(row for row in removed if row["strategy_id"] not in already)
        log["removed"].sort(key=lambda row: row["strategy_id"].casefold())
        tmp = REMOVED_DUPLICATES_LOG + ".tmp"
        with io.open(tmp, "w", encoding="utf-8") as handle:
            json.dump(log, handle, indent=2, ensure_ascii=False, sort_keys=True)
            handle.write(u"\n")
        os.replace(tmp, REMOVED_DUPLICATES_LOG)
    print(u"%d duplicate source file(s) removed" % len(removed), flush=True)
    return removed


def refresh_intake_evidence(fresh_repos=None):
    """Refresh all source-derived intake artifacts, never measurements."""
    print(u"refreshing canonical execution profiles...", flush=True)
    if execution_profiles.main([]) != 0:
        return 1
    print(u"checking for and removing semantic duplicates...", flush=True)
    if remove_semantic_duplicates(fresh_repos):
        print(u"refreshing canonical execution profiles (post-removal)...", flush=True)
        if execution_profiles.main([]) != 0:
            return 1
    print(u"refreshing strategy classification...", flush=True)
    if strategy_classification.main([]) != 0:
        return 1
    print(u"labelling new strategies (logic labels, second opinion where required)...", flush=True)
    label_intake.main([])  # never fatal: an unreachable model leaves rows for the next intake
    print(u"refreshing preregistered phase hypotheses...", flush=True)
    if market_phase_hypothesis.main([]) != 0:
        return 1
    print(u"refreshing semantic duplicate evidence...", flush=True)
    if semantic_duplicates.main([]) != 0:
        return 1
    print(u"refreshing generated status and status page...", flush=True)
    if strategy_status.main([]) != 0:
        return 1
    return strategy_status_page.main([])


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Harvest strategy source files and refresh intake evidence.")
    parser.add_argument("--no-refresh", action="store_true",
                        help="download only; skip profile and duplicate evidence refresh")
    parser.add_argument("targets", nargs="+", help="GitHub repositories as owner/repo")
    args = parser.parse_args(argv)
    targets = args.targets
    base = set()
    for x in sorted(os.listdir(REPOS)):
        p = os.path.join(REPOS, x)
        if os.path.isdir(p):
            base |= {n for _f, n in find_strategies(p)}
    print(u"unique classes before fetch: %d" % len(base), flush=True)
    grand = set(base)
    added = 0
    fetched = set()
    for full in targets:
        name, got, cls, err = harvest(full)
        if err and got == 0:
            print(u"  ✗ %-46s %s" % (name, err), flush=True)
            continue
        fetched.add(full.replace("/", "_", 1))
        p = os.path.join(REPOS, full.replace("/", "_", 1))
        names = {n for _f, n in find_strategies(p)}
        new = names - grand
        grand |= names
        added += len(new)
        print(u"  %-46s files %3d · classes %3d · NEW %3d%s"
              % (name, got, len(names), len(new),
                 (u"  [%s]" % err) if err else u""), flush=True)
    print()
    print(u"unique classes now: %d (increase %d)"
          % (len(grand), len(grand) - len(base)))
    if added and not args.no_refresh:
        if refresh_intake_evidence(fetched) != 0:
            print(u"harvest succeeded but intake evidence refresh failed", file=sys.stderr)
            return 1
    elif added:
        print(u"new classes downloaded; evidence refresh skipped by --no-refresh")
    else:
        print(u"no new classes; intake evidence already remains current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
