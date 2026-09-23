# -*- coding: utf-8 -*-
"""Record the FrequentHippo strategy feed as a Stage-0 discovery source.

The feed is an automated index of GitHub Python files, not a quality signal.
This module fetches only its public metadata and the immutable GitHub raw
revision named by each post.  It never writes a strategy under ``repos/``,
never invokes :mod:`tools.harvest`, and never starts a measurement.  A record
marked ``candidate_requires_review`` is therefore only a manually reviewable
lead, not an admission or a download instruction.

The generated report pins every observed source to ``owner/repo``, commit and
path.  This matters because ``tools.harvest owner/repo`` intentionally reads a
repository's current default branch; using it after a feed observation is a
new, explicit acquisition decision rather than a silent substitution of the
feed revision.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import html
import io
import json
import os
import re
import sys
import time
import warnings
from datetime import datetime, timezone
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import unquote
from urllib.request import Request, urlopen


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS = os.path.join(ROOT, "STRATEGY_STATUS.csv")
OUTPUT_JSON = os.path.join(ROOT, "evidence", "STRATEGY_FEED.json")
OUTPUT_MD = os.path.join(ROOT, "evidence", "STRATEGY_FEED.md")
FEED_URL = "https://frequenthippo.ddns.net/category/strategy-feed/"
POSTS_URL = "https://frequenthippo.ddns.net/wp-json/wp/v2/posts"
CATEGORY_ID = 8
USER_AGENT = "strategy-audit-stage0/1.0 (+https://github.com/M1ch43lV/strategy-audit)"
RAW_RE = re.compile(
    r"https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/([^\"<]+)"
)
FIXTURE_RE = re.compile(r"(?:^|/)(?:test|tests|smoke|evaluation|baseline|sample|demo)(?:/|$)|candidate", re.I)


def fetch_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:  # nosec B310 - fixed HTTPS sources
                return response.read()
        except HTTPError:
            raise
        except URLError:
            if attempt == 2:
                raise
            time.sleep(0.25 * (attempt + 1))
    raise AssertionError("unreachable")


def source_reference(rendered: str) -> dict[str, str] | None:
    match = RAW_RE.search(html.unescape(rendered or ""))
    if not match:
        return None
    owner, repository, commit, path = match.groups()
    path = unquote(path)
    return {
        "repository": "%s/%s" % (owner, repository),
        "commit": commit,
        "path": path,
        "url": match.group(0),
    }


def is_istrategy_base(base: ast.expr) -> bool:
    if isinstance(base, ast.Name):
        return base.id == "IStrategy"
    return isinstance(base, ast.Attribute) and base.attr == "IStrategy"


def strategy_classes(source: bytes) -> tuple[list[str], str | None]:
    try:
        with warnings.catch_warnings():
            # A fetched feed file is third-party text; invalid escape sequences
            # in it are expected and are not ours to repair.
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(source.decode("utf-8-sig", "replace"))
    except SyntaxError as exc:
        return [], "syntax_error: %s" % exc.msg
    return [node.name for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
            and any(is_istrategy_base(base) for base in node.bases)], None


def known_corpus() -> tuple[set[str], set[str]]:
    names: set[str] = set()
    paths: set[str] = set()
    with io.open(STATUS, encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            names.add((row.get("strategy_id") or "").casefold())
            source = (row.get("source_file") or "").replace("\\", "/")
            paths.add(re.sub(r"^repair/patched/", "", source,
                             flags=re.IGNORECASE).casefold())
    return names, paths


def classify(reference: dict[str, str], classes: list[str], error: str | None,
             known_names: set[str], known_paths: set[str]) -> str:
    path = reference["path"]
    if reference["repository"].casefold() == "m1ch43lv/strategy-audit":
        local_path = os.path.normpath(os.path.join(ROOT, path))
        if (os.path.commonpath((ROOT, local_path)) == ROOT
                and os.path.isfile(local_path)):
            return "local_audit_source"
    normalized_path = re.sub(r"^repair/patched/", "", path,
                             flags=re.IGNORECASE).casefold()
    if normalized_path in known_paths:
        return "known_source_path"
    if error:
        return "source_parse_error"
    if not classes:
        return "non_strategy_fixture"
    if all(name.casefold() in known_names for name in classes):
        return "known_class_name"
    if FIXTURE_RE.search(path):
        return "fixture_or_scaffold_requires_review"
    return "candidate_requires_review"


def collect(posts: Iterable[dict[str, Any]], known_names: set[str],
            known_paths: set[str], read=fetch_bytes) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for post in posts:
        reference = source_reference(((post.get("content") or {}).get("rendered") or ""))
        record: dict[str, Any] = {
            "post_id": post.get("id"),
            "feed_date": post.get("date"),
            "feed_title": ((post.get("title") or {}).get("rendered") or ""),
            "feed_post_url": post.get("link"),
        }
        if not reference:
            record["review_status"] = "missing_pinned_github_source"
            records.append(record)
            continue
        record.update(reference)
        try:
            source = read(reference["url"])
        except (OSError, URLError) as exc:
            record["review_status"] = "source_fetch_error"
            record["source_error"] = str(exc)
            records.append(record)
            continue
        classes, error = strategy_classes(source)
        record["source_sha256"] = hashlib.sha256(source).hexdigest()
        record["strategy_classes"] = classes
        if error:
            record["source_error"] = error
        record["known_classes"] = [name for name in classes
                                   if name.casefold() in known_names]
        record["review_status"] = classify(reference, classes, error,
                                           known_names, known_paths)
        records.append(record)
    return records


def fetch_posts(limit: int) -> list[dict[str, Any]]:
    query = ("%s?categories=%d&per_page=%d&orderby=date&order=desc&"
             "_fields=id,date,link,title,content" % (POSTS_URL, CATEGORY_ID, limit))
    try:
        payload = json.loads(fetch_bytes(query).decode("utf-8"))
    except (OSError, URLError, ValueError) as exc:
        raise RuntimeError("could not fetch strategy feed: %s" % exc) from exc
    if not isinstance(payload, list):
        raise RuntimeError("strategy feed returned a non-list payload")
    return payload


def report(records: list[dict[str, Any]], observed_at: str) -> bytes:
    counts: dict[str, int] = {}
    for record in records:
        status = record["review_status"]
        counts[status] = counts.get(status, 0) + 1
    lines = [
        "# Strategy feed intake - review-only Stage 0 leads", "",
        "**Generated by `evidence/strategy_feed.py`.** The FrequentHippo feed is an",
        "automated discovery index, not a quality, safety, compatibility, or profitability",
        "verdict. It never imports sources or starts a benchmark.", "",
        "- Feed: `%s`" % FEED_URL,
        "- Observed at: `%s`" % observed_at,
        "- Posts inspected: %d" % len(records), "",
        "## Review statuses", "", "| Status | Posts | Meaning |", "|---|---:|---|",
    ]
    meanings = {
        "known_source_path": "The pinned source path is already in the corpus.",
        "local_audit_source": "The pinned file is already present in this audit repository.",
        "known_class_name": "A class of this name already exists; inspect for a real implementation difference.",
        "non_strategy_fixture": "The pinned file defines no IStrategy class.",
        "fixture_or_scaffold_requires_review": "An IStrategy class occurs in a test, sample, baseline, demo, or candidate path.",
        "candidate_requires_review": "A new IStrategy class; manual provenance and suitability review is still required.",
        "source_parse_error": "The pinned source could not be parsed as Python.",
        "source_fetch_error": "The pinned source could not be read; retry before deciding.",
        "missing_pinned_github_source": "The post lacks a GitHub raw commit URL.",
    }
    for status in sorted(counts):
        lines.append("| `%s` | %d | %s |" % (status, counts[status], meanings[status]))
    candidates = [record for record in records
                  if record["review_status"] == "candidate_requires_review"]
    lines += ["", "## New IStrategy leads - %d" % len(candidates), ""]
    if candidates:
        lines += ["| Feed date | Repository | Commit | Class | Path |",
                  "|---|---|---|---|---|"]
        for record in candidates:
            lines.append("| %s | `%s` | `%s` | `%s` | `%s` |" % (
                record.get("feed_date", "-"), record["repository"],
                record["commit"], ", ".join(record.get("strategy_classes", [])),
                record["path"]))
    else:
        lines.append("None.")
    lines += ["", "## Required next step", "",
              "A reviewer must inspect a candidate's pinned source and upstream repository, then",
              "explicitly decide whether to acquire that repository with `python -m tools.harvest`,",
              "which captures the repository's then-current default branch. That later acquisition",
              "is deliberately separate from this feed observation and follows the normal Stage 0",
              "malware gate, canonicalization, and duplicate adjudication.", ""]
    return "\n".join(lines).encode("utf-8")


def write_records(records: list[dict[str, Any]], observed_at: str) -> None:
    payload = {"schema_version": 1, "feed": FEED_URL, "observed_at": observed_at,
               "records": records}
    for path, body in ((OUTPUT_JSON, json.dumps(payload, indent=2, ensure_ascii=False,
                                                 sort_keys=True).encode("utf-8") + b"\n"),
                       (OUTPUT_MD, report(records, observed_at))):
        temporary = path + ".tmp"
        with open(temporary, "wb") as handle:
            handle.write(body)
        os.replace(temporary, path)


def selftest() -> None:
    rendered = '<a href="https://raw.githubusercontent.com/example/strategies/%s/user_data/strategies/Fresh.py">Source</a>' % ("a" * 40)
    posts = [{"id": 1, "date": "2026-09-22T00:00:00", "link": "https://feed/post",
              "title": {"rendered": "Fresh"}, "content": {"rendered": rendered}},
             {"id": 2, "date": "2026-09-22T00:00:01", "link": "https://feed/test",
              "title": {"rendered": "Fixture"}, "content": {"rendered":
              '<a href="https://raw.githubusercontent.com/example/strategies/%s/tests/Test.py">Source</a>' % ("b" * 40)}}]
    source = b"from freqtrade.strategy import IStrategy\nclass Fresh(IStrategy):\n    pass\n"
    records = collect(posts, set(), set(), read=lambda _url: source)
    assert records[0]["review_status"] == "candidate_requires_review"
    assert records[0]["strategy_classes"] == ["Fresh"]
    assert records[1]["review_status"] == "fixture_or_scaffold_requires_review"
    assert source_reference("no source") is None
    print("strategy feed selftest: PASS")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--limit", type=int, default=100,
                        help="newest feed posts to inspect (1-100, default: 100)")
    parser.add_argument("--write", action="store_true",
                        help="write evidence/STRATEGY_FEED.{json,md}; otherwise print a summary only")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    if not 1 <= args.limit <= 100:
        parser.error("--limit must be between 1 and 100")
    known_names, known_paths = known_corpus()
    records = collect(fetch_posts(args.limit), known_names, known_paths)
    counts: dict[str, int] = {}
    for record in records:
        counts[record["review_status"]] = counts.get(record["review_status"], 0) + 1
    print("strategy feed posts=%d %s" % (
        len(records), " ".join("%s=%d" % item for item in sorted(counts.items()))))
    if args.write:
        observed_at = datetime.now(timezone.utc).isoformat()
        write_records(records, observed_at)
        print("wrote %s, %s" % (OUTPUT_JSON, OUTPUT_MD))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
