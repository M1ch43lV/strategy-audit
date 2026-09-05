# -*- coding: utf-8 -*-
"""Has any source repository this corpus already draws from moved since we
captured it, and does `corpus_sources.json` know about a repo that was
harvested but never made it into the audited pipeline.

Two different questions, both about staleness of a different kind:

REPO DRIFT. Every strategy here is a snapshot - a local git clone or, for
four oversized repositories, a `harvest.py` file-by-file fetch - taken once.
Nothing re-checks it against upstream afterward, so a bug fix landing in the
author's repo six months later is invisible unless someone asks. This module
asks, for every repo currently contributing at least one strategy_id to
`STRATEGY_STATUS.csv`.

The comparison is not simply "local HEAD vs. remote HEAD": several repos
carry a repair commit on top of the real clone (a Russian-to-English
translation, a NumPy-compatibility fix) applied and committed locally by this
project's own tooling and never pushed anywhere. Diffing THAT commit against
GitHub always 404s - GitHub has never seen it - which says nothing about
whether the upstream repo moved. `upstream_head()` walks back past any such
commit to the newest one GitHub can also produce, and compares from there.

HARVESTED BUT NEVER INTEGRATED. `corpus_sources.json` records 53 repos this
project has at some point pulled `.py` files from and scanned for
`IStrategy` classes, keyed with a `first` count - how many of that repo's
classes were the first occurrence of their name across the whole scan, in
whatever order the repos were processed. A repo can sit in that file with
`first=0` and never have contributed anything a human decided was worth
admitting; one with `first>0` was found to add unique classes and still
never reached `EXECUTION_PROFILES.csv`, which is a gap this file surfaces
rather than a fact anyone had already read off six different JSON stores.

Neither section decides anything. A repo shown as `ahead` is a candidate for
a deliberate, later re-fetch - never a silent swap of files this audit's
900 canonical_sha256 values are pinned to.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import subprocess


ROOT = os.path.dirname(os.path.abspath(__file__))
STATUS = os.path.join(ROOT, "STRATEGY_STATUS.csv")
PROFILES = os.path.join(ROOT, "EXECUTION_PROFILES.csv")
CORPUS_SOURCES = os.path.join(ROOT, "corpus_sources.json")
REPOS_DIR = os.path.join(ROOT, "repos")
OUTPUT_CSV = os.path.join(ROOT, "REPO_FRESHNESS.csv")
OUTPUT_MD = os.path.join(ROOT, "REPO_FRESHNESS.md")

FIELDS = [
    "repo", "local_kind", "local_only_patch_commit", "local_sha", "local_date",
    "remote_default_branch", "remote_head_sha", "remote_pushed_at",
    "remote_status", "ahead_by", "behind_by",
]


def repos_in_use():
    with io.open(STATUS, encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return sorted({row["repo"] for row in rows if row["repo"]})


def local_dir(repo):
    return os.path.join(REPOS_DIR, repo.replace("/", "_", 1))


def is_git(path):
    return os.path.isdir(os.path.join(path, ".git"))


def _git(path, *args):
    out = subprocess.run(["git", "-C", path] + list(args), capture_output=True,
                        timeout=20, encoding="utf-8", errors="replace")
    return out.stdout if out.returncode == 0 else ""


def git_log_shas(path, limit=30):
    text = _git(path, "log", "-n", str(limit), "--format=%H|%aI")
    lines = [line.split("|", 1) for line in text.strip().splitlines() if line]
    return [(sha, date) for sha, date in lines]


def gh_api(path):
    out = subprocess.run(["gh", "api", path], capture_output=True, timeout=60)
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout.decode("utf-8", "replace"))
    except ValueError:
        return None


def upstream_head(repo, path):
    """The newest local commit GitHub also has - see the module docstring."""
    for sha, date in git_log_shas(path):
        if gh_api("repos/%s/commits/%s" % (repo, sha)) is not None:
            return sha, date
    return None, None


def newest_mtime(path):
    newest = 0.0
    for dirpath, _dirs, files in os.walk(path):
        if ".git" in dirpath.split(os.sep):
            continue
        for name in files:
            try:
                newest = max(newest, os.path.getmtime(os.path.join(dirpath, name)))
            except OSError:
                pass
    return newest


def check_repo(repo):
    path = local_dir(repo)
    row = {"repo": repo}
    if not os.path.isdir(path):
        row.update({"local_kind": "missing"})
    elif is_git(path):
        shas = git_log_shas(path, limit=1)
        head_sha = shas[0][0] if shas else None
        sha, date = upstream_head(repo, path)
        row.update({"local_kind": "git_clone", "local_sha": sha,
                   "local_date": date, "local_only_patch_commit": sha != head_sha})
    else:
        mtime = newest_mtime(path)
        row.update({"local_kind": "harvest_files",
                   "local_date": (
                       __import__("datetime")
                       .datetime.fromtimestamp(mtime, __import__("datetime").timezone.utc)
                       .isoformat() if mtime else None)})

    meta = gh_api("repos/%s" % repo)
    if meta is None:
        row["remote_status"] = "api_error_or_not_found"
        return row
    branch = meta.get("default_branch", "main")
    row.update({"remote_default_branch": branch,
               "remote_pushed_at": meta.get("pushed_at")})
    tip = gh_api("repos/%s/commits/%s" % (repo, branch))
    if tip:
        row["remote_head_sha"] = tip.get("sha")

    if row.get("local_sha") and row.get("remote_head_sha"):
        if row["local_sha"] == row["remote_head_sha"]:
            row["remote_status"] = "current"
        else:
            cmp_ = gh_api("repos/%s/compare/%s...%s" % (repo, row["local_sha"], branch))
            if cmp_:
                row["remote_status"] = cmp_.get("status")
                row["ahead_by"] = cmp_.get("ahead_by")
                row["behind_by"] = cmp_.get("behind_by")
            else:
                row["remote_status"] = "differs_compare_failed"
    elif row.get("local_date") and row.get("remote_pushed_at"):
        row["remote_status"] = ("current_by_pushed_at"
                                if row["remote_pushed_at"] <= row["local_date"]
                                else "pushed_after_local_fetch")
    else:
        row["remote_status"] = "unknown"
    return row


def repos_from_original_file():
    """Every repo actually feeding a canonical strategy, read off provenance
    that survives a repair overlay.

    `STRATEGY_STATUS.csv`'s own `repo` column is blank wherever a row's
    canonical file was replaced by a repaired copy under
    `user_data/profile_repairs/` - the repair carries no `repos/` marker for
    `strategy_status.provenance()` to read. `EXECUTION_PROFILES.csv`'s
    `original_file` always names the pre-repair source, so a repo is "in use"
    if EITHER column says so. Without this, `FTT_DWT_FBB_FUTURES` - canonical
    file repaired, original file in `Lijunnan0113/...` - reads as a repo this
    corpus has never touched, when it has been in it all along.
    """
    found = set(repos_in_use())
    if not os.path.exists(PROFILES):
        return found
    with io.open(PROFILES, encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            path = (row.get("original_file") or "").replace("\\", "/")
            marker = "repos/"
            index = path.find(marker)
            if index < 0:
                continue
            stem = path[index + len(marker):].split("/")[0]
            owner, _sep, name = stem.partition("_")
            if name:
                found.add("%s/%s" % (owner, name))
    return found


def harvested_not_integrated():
    """Repos `corpus_sources.json` scanned that never reached the pipeline.

    `first` counts classes credited as the earliest occurrence of their name
    in whatever order the harvesting ran; a repo can hold `first=0` and have
    added nothing a human chose to keep, or `first>0` and simply never have
    been carried the rest of the way to `EXECUTION_PROFILES.csv`.
    """
    if not os.path.exists(CORPUS_SOURCES):
        return []
    data = json.load(io.open(CORPUS_SOURCES, encoding="utf-8"))
    in_pipeline = repos_from_original_file()
    return [entry for entry in data.get("repos", [])
            if entry["repo"] not in in_pipeline]


def _csv_bytes(rows):
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n",
                            extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue().encode("utf-8")


def _report(rows, unintegrated):
    ahead = [r for r in rows if r.get("remote_status") == "ahead"]
    lines = [
        "# Repo freshness - has any source moved since we captured it", "",
        "**Generated by `repo_freshness.py`.** A live comparison against "
        "GitHub, not derived from anything else in this repo; regenerate "
        "rather than editing.", "",
        "Deciding anything from a row here means a deliberate, later "
        "re-fetch of that one repo - never a silent swap of the files this "
        "audit's `canonical_sha256` values are pinned to.", "",
        "## Repos already in the corpus - %d checked" % len(rows), "",
        "| Repo | Status | Ahead by | Pushed |", "|---|---|---:|---|",
    ]
    for row in sorted(rows, key=lambda r: r["repo"]):
        lines.append("| `%s` | %s | %s | %s |" % (
            row["repo"], row.get("remote_status", "-"),
            row.get("ahead_by", "-") or "-", row.get("remote_pushed_at", "-")))
    lines += ["", "### Ahead of our capture - %d" % len(ahead), ""]
    if ahead:
        for row in ahead:
            lines.append("- `%s` - %s commits ahead, pushed %s" % (
                row["repo"], row.get("ahead_by"), row.get("remote_pushed_at")))
    else:
        lines.append("None.")
    lines += [
        "", "## Harvested but never integrated - %d" % len(unintegrated), "",
        "In `corpus_sources.json` (this project scanned it for classes at "
        "some point) but absent from `STRATEGY_STATUS.csv`'s own repo list "
        "(no canonical file from it ever reached `EXECUTION_PROFILES.csv`).",
        "", "| Repo | Classes found | First-occurrence classes |",
        "|---|---:|---:|",
    ]
    for entry in sorted(unintegrated, key=lambda e: -e["first"]):
        lines.append("| `%s` | %d | %d%s |" % (
            entry["repo"], entry["classes"], entry["first"],
            " ← unique, never admitted" if entry["first"] > 0 else ""))
    lines.append("")
    return "\n".join(lines).encode("utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", action="append", default=[],
                        help="check only these repos, not the full corpus list")
    args = parser.parse_args(argv)
    repos = args.repo or repos_in_use()
    rows = []
    for repo in repos:
        row = check_repo(repo)
        rows.append(row)
        print("%-58s %-22s ahead=%s pushed=%s" % (
            repo, row.get("remote_status"), row.get("ahead_by", "-"),
            row.get("remote_pushed_at")), flush=True)
    if not args.repo:
        unintegrated = harvested_not_integrated()
        with io.open(OUTPUT_CSV, "wb") as handle:
            handle.write(_csv_bytes(rows))
        with io.open(OUTPUT_MD, "wb") as handle:
            handle.write(_report(rows, unintegrated))
        print("\nwrote %s, %s" % (OUTPUT_CSV, OUTPUT_MD))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
