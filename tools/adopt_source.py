# -*- coding: utf-8 -*-
"""adopt_source - bring in a strategy that was published without a repository.

WHY A SECOND WRITER EXISTS. `tools/harvest.py` is the intake for repositories:
it reads the GitHub API and writes below `repos/`. A strategy its author
published on a page and never in a repository cannot be reached that way, and
Stage 0 reserves `repos/` for harvest. The owner decided on 2026-09-24
(`PIPELINE_EXTENSIONS.md` Part 5) that such a file is adopted by one explicit
command per file, into one folder per source, and that it then enters the corpus
like any other strategy - same malware gate, same duplicate adjudication, same
representative rule, same population rules. The folder is the attribution: the
profile table reports `repo` from the directory name, so an adopted strategy
appears as this source's own, exactly as a repository's does.

WHAT THIS COMMAND IS NOT. No crawler and no bulk path - one URL per call, and
the call is the acquisition event, the way `harvest owner/repo` is one. The tag
is a source label, never a quality signal. Nothing here decides whether a
strategy is good; that is what the measurement chain is for.

WHAT IT REFUSES. A file that is not a strategy by the corpus's own definition
(`tools.harness.find_strategies`, IStrategy inheritance - not a second
definition written here), a file the malware gate matches, a URL that does not
end in a single `.py` name, a source tag no one decided on, and a second copy of
the same path with a different hash unless `--replace` says so out loud. A class
whose base is another local class instead of `IStrategy` is refused too; the
corpus knows that shape (`EXTRA_SUBCLASS_STRATEGIES`) and admitting one stays an
explicit decision rather than a side effect of a download.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

_ROOT = (os.environ.get("AUDIT_ROOT") or
         os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from tools import malware_gate
from tools.harness import find_strategies

REPOS = os.path.join(_ROOT, "repos")
# One folder per non-repository source. A new name here is an owner decision and
# a line in `PIPELINE_EXTENSIONS.md` Part 5, not a command-line convenience: the
# folder name is what every report will show as the strategy's origin.
ALLOWED_SOURCES = ("frequenthippo",)
PROVENANCE = ".sources.json"
MAX_FILE = 600000
# Windows forbids `<>:"|?*` in a path segment and a percent-escaped name is a
# smell, not a strategy name. `tools/harvest.py` has to rewrite such segments
# because a repository's tree is fixed; here the name comes from an argument, so
# a name outside this set is refused instead of sanitised.
SAFE_NAME = re.compile(r"^[A-Za-z0-9_ .()+-]+\.py$")
USER_AGENT = "strategy-audit-adopt/1.0 (+https://github.com/M1ch43lV/strategy-audit)"


def fetch(url):
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=60) as response:  # nosec B310 - a URL the caller names
        return response.read()


def destination(source, url):
    """`repos/<source>/<basename>`, or a refusal. A URL never contributes a path.

    Only the last path segment is used and it has to be one plain `.py` name, so
    a query string, a fragment or a `../` segment cannot place a file outside
    the source folder.
    """
    if source not in ALLOWED_SOURCES:
        raise SystemExit("refusing source %r: allowed sources are %s - a new one "
                         "is an owner decision, not an argument"
                         % (source, ", ".join(ALLOWED_SOURCES)))
    name = url.split("?")[0].split("#")[0].rstrip("/").rsplit("/", 1)[-1]
    if not SAFE_NAME.match(name) or name == ".py":
        raise SystemExit("refusing %r: the URL must end in one plain '.py' file name" % url)
    return os.path.join(REPOS, source, name)


def strategy_error(body, strategy):
    """None when `body` defines `strategy`, otherwise why it does not.

    The definition is the corpus's own (`tools.harness.find_strategies`), so an
    adopted file cannot be measured as a strategy that the rest of the chain
    would not recognise as one.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "candidate.py")
        with io.open(path, "wb") as handle:
            handle.write(body)
        names = {name for _file, name in find_strategies(tmp)}
    if not names:
        return "no class with an IStrategy base in the file"
    if strategy not in names:
        return ("the file defines %s, not %s - an indirect base is the corpus's "
                "EXTRA_SUBCLASS_STRATEGIES case and needs its own decision"
                % (", ".join(sorted(names)[:4]), strategy))
    return None


def record_provenance(source_dir, entry):
    """Append one adoption to `<source_dir>/<PROVENANCE>`.

    It sits next to the files on purpose: it belongs to the source, not to a
    read model, and no consumer of `repos/` reads it (`find_strategies` and
    `execution_profiles.discover()` look at `.py` only). It is the only place
    that records which URL a file came from, because a web page has no commit to
    pin - the stored bytes are the identity, and a later change of the page is a
    new hash, never an overwrite of this record.
    """
    path = os.path.join(source_dir, PROVENANCE)
    entries = []
    if os.path.exists(path):
        try:
            entries = json.load(io.open(path, encoding="utf-8")).get("adoptions") or []
        except (ValueError, OSError):
            entries = []
    entries.append(entry)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump({"schema_version": 1, "adoptions": entries}, handle,
                  indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)
    return path


def sha256(body):
    return "sha256_" + hashlib.sha256(body).hexdigest()


def selftest():
    cases = 0
    target = destination("frequenthippo", "https://example.invalid/a/b/Name.py?x=1#frag")
    assert target == os.path.join(REPOS, "frequenthippo", "Name.py"), target
    cases += 1
    # Only the last segment becomes a file name, so a `..` earlier in the path
    # cannot escape the source folder - that is the point of the check below.
    escape = destination("frequenthippo", "https://example.invalid/a/../Name.py")
    assert escape == os.path.join(REPOS, "frequenthippo", "Name.py"), escape
    cases += 1
    for bad in ("https://example.invalid/a/b/", "https://example.invalid/a/b/Name.txt",
                "https://example.invalid/a/b/Name*.py",
                "https://example.invalid/a/b/%2e%2e%2fName.py"):
        try:
            destination("frequenthippo", bad)
        except SystemExit:
            cases += 1
        else:
            raise AssertionError("accepted %r" % bad)
    try:
        destination("someone-else", "https://example.invalid/Name.py")
    except SystemExit:
        cases += 1
    else:
        raise AssertionError("accepted an undecided source tag")
    good = (b"from freqtrade.strategy import IStrategy\n\n\n"
            b"class Mine(IStrategy):\n    timeframe = '5m'\n")
    assert strategy_error(good, "Mine") is None
    assert strategy_error(good, "Other") is not None
    assert strategy_error(b"x = 1\n", "Mine") is not None
    cases += 3
    with tempfile.TemporaryDirectory() as tmp:
        record_provenance(tmp, {"url": "a", "sha256": "h1"})
        record_provenance(tmp, {"url": "a", "sha256": "h2"})
        data = json.load(io.open(os.path.join(tmp, PROVENANCE), encoding="utf-8"))
        assert [row["sha256"] for row in data["adoptions"]] == ["h1", "h2"], data
    cases += 1
    assert sha256(b"") == ("sha256_e3b0c44298fc1c149afbf4c8996fb924"
                           "27ae41e4649b934ca495991b7852b855"), sha256(b"")
    cases += 1
    print("adopt_source selftest: PASS (%d cases)" % cases)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Adopt one strategy file that has no repository.")
    parser.add_argument("--url", help="the published file to adopt")
    parser.add_argument("--strategy", help="the class the file must define")
    parser.add_argument("--source", default=ALLOWED_SOURCES[0],
                        help="source folder under repos/ (default: %s)" % ALLOWED_SOURCES[0])
    parser.add_argument("--reason", default="",
                        help="why this file, and why no repository - recorded")
    parser.add_argument("--replace", action="store_true",
                        help="overwrite an existing file whose hash differs")
    parser.add_argument("--dry-run", action="store_true",
                        help="fetch and verify, write nothing")
    parser.add_argument("--no-refresh", action="store_true",
                        help="skip the intake refresh after writing")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.url or not args.strategy:
        parser.error("--url and --strategy are required (or --selftest)")

    target = destination(args.source, args.url)
    try:
        body = fetch(args.url)
    except (HTTPError, URLError, OSError) as exc:
        print("FAILED to fetch %s: %s" % (args.url, exc))
        return 1
    if len(body) >= MAX_FILE:
        print("REFUSED: %d bytes is at or above the %d-byte limit for one file"
              % (len(body), MAX_FILE))
        return 1
    hits = malware_gate.scan_bytes(body)
    if hits:
        print("REFUSED by malware_gate: %s"
              % ", ".join(sorted({name for _line, name in hits})))
        return 1
    error = strategy_error(body, args.strategy)
    if error:
        print("REFUSED: %s" % error)
        return 1

    digest = sha256(body)
    if os.path.exists(target):
        with io.open(target, "rb") as handle:
            stored = sha256(handle.read())
        if stored == digest:
            print("%s is already in the corpus with these bytes (%s) - nothing written"
                  % (os.path.relpath(target, _ROOT).replace(os.sep, "/"), digest[:19]))
            return 0
        if not args.replace:
            print("REFUSED: %s exists with %s, the download has %s - pass --replace "
                  "if the newer publication should take its place"
                  % (os.path.relpath(target, _ROOT).replace(os.sep, "/"),
                     stored[:19], digest[:19]))
            return 1

    relative = os.path.relpath(target, _ROOT).replace(os.sep, "/")
    print("%s -> %s (%d bytes, %s)" % (args.url, relative, len(body), digest[:19]))
    if args.dry_run:
        print("dry run: nothing written, no intake refresh")
        return 0
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with io.open(target, "wb") as handle:
        handle.write(body)
    record_provenance(os.path.dirname(target), {
        "url": args.url,
        "strategy": args.strategy,
        "source": args.source,
        "sha256": digest,
        "bytes": len(body),
        "adopted_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "reason": args.reason,
    })
    if args.no_refresh:
        print("adopted; evidence refresh skipped by --no-refresh")
        return 0
    from tools.harvest import refresh_intake_evidence
    print("refreshing intake evidence...", flush=True)
    # The source folder counts as freshly fetched, exactly like a repository
    # harvest passes its own names: the intake rule may then remove an adopted
    # file that turns out to be a code-identical copy of a strategy that no
    # check has looked at yet. Without this the copy would stay on disk as a
    # second file of a strategy that is already represented - the case the
    # owner's rule of 2026-09-16 puts at intake on purpose.
    return refresh_intake_evidence({os.path.basename(os.path.dirname(target))})


if __name__ == "__main__":
    sys.exit(main())
