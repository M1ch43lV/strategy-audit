# -*- coding: utf-8 -*-
"""source_dates - three real dates per strategy, and no invented publication date.

WHY NOT "PUBLICATION DATE". The corpus was harvested: the 83 directories under
`repos/` carry no `.git` of their own (checked 2026-09-24), so no commit history
of the authors is available locally, and the third-party site publishes no date
per version either. What *is* available are three different facts, and calling
any of them "the publication date" would be wrong for most strategies:

* `name` - a date the author or the generator wrote into the class name
  (`E0V1E_20230915`, `GeneTrader_gen9_1735161895_5455`, `..._20211008`). The
  author's own statement, and the only one that dates the *revision*.
* `site` - the WordPress post date of the file taken from the published site.
  That is when the site published it, which is a real publication, just not the
  author's.
* `upstream` - the last commit that touched the file in the repository it was
  harvested from, read through the GitHub API. For a repository with its own
  history this is close to the date of the revision (Foxel05/freqtrade-stuff
  BinHV45: 2021-10-12). For a bulk mirror it is the date of the import: every
  file of `remiotore/ccxt-freqtrade` - 74 % of the corpus - reports the same
  2025-09-10, and the store therefore records per repository whether its dates
  are one import date (`bulk_import`), so the page can say so instead of
  implying that a strategy was written that day.

The store is a resumable cache with one writer, this program. Nothing else reads
or writes it, an entry is never guessed, and a strategy with no date of any kind
simply has none. The GitHub API allows 60 requests an hour without a token and
5000 with one; a token is read from `GITHUB_TOKEN`, `GH_TOKEN` or the
gitignored file `user_data/.github_token`, never from a command line, so it
cannot end up in a shell history or in this repository. A run that hits the rate
limit stops cleanly and says when it may continue.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

_ROOT = (os.environ.get("AUDIT_ROOT") or
         os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from tools.strategy_ideas import date_in_name, family_members, load_profiles

PROFILES = os.path.join(_ROOT, "evidence", "EXECUTION_PROFILES.csv")
IDEAS = os.path.join(_ROOT, "evidence", "STRATEGY_IDEAS.json")
STORE = os.path.join(_ROOT, "evidence", "SOURCE_DATES.json")
TOKEN_FILE = os.path.join(_ROOT, "user_data", ".github_token")
API = "https://api.github.com"
SITE = "https://frequenthippo.ddns.net"
USER_AGENT = "strategy-audit-source-dates"
# A repository whose checked files all share one commit date is an import, not
# a history; the threshold keeps a small, genuinely uniform repository from
# being labelled from too little evidence.
BULK_MIN_FILES = 5


def upstream_path(row):
    """`repos/<owner_repo>/strategies/X.py` -> `strategies/X.py`, else ''.

    The corpus keeps the repository and the path inside it in one column, and the
    repository directory name is the owner and the name joined by `_`, so the
    prefix to strip is derived rather than guessed.
    """
    original = (row.get("original_file") or "").replace("\\", "/")
    repo = row.get("repo") or ""
    prefix = "repos/%s/" % repo.replace("/", "_")
    if original.startswith(prefix):
        return original[len(prefix):]
    return ""


def token():
    """From the environment first, then from the gitignored file - never argv."""
    for name in ("GITHUB_TOKEN", "GH_TOKEN"):
        value = (os.environ.get(name) or "").strip()
        if value:
            return value
    if os.path.exists(TOKEN_FILE):
        return io.open(TOKEN_FILE, encoding="utf-8").read().strip() or None
    return None


def _get(url, tok=None, timeout=25):
    """(status, headers, text). 404 and rate limits are answers, not crashes."""
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json",
    })
    if tok:
        request.add_header("Authorization", "Bearer %s" % tok)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, dict(response.headers), response.read().decode(
                "utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers or {}), exc.read().decode("utf-8", "replace")
    except Exception as exc:                                   # network down, DNS
        return 0, {}, str(exc)


def rate_limit(tok=None):
    """The API's own report on the caller's budget - this endpoint costs no quota.

    It is what tells a run apart from a guess: 60 requests an hour is an
    anonymous caller, 5000 is a token, and a token that has expired or lost its
    grant shows up here as 60 again rather than as a failure halfway through.
    """
    status, _headers, text = _get("%s/rate_limit" % API, tok)
    if status != 200:
        return None
    try:
        return (json.loads(text).get("resources") or {}).get("core") or None
    except ValueError:
        return None


def github_commit(repo, path, tok=None):
    """The last commit that touched `path` in `repo`, or a stated reason why not."""
    if not repo or "/" not in repo or not path:
        return {"error": "no repository path"}
    url = "%s/repos/%s/commits?path=%s&per_page=1" % (API, repo, urllib.parse.quote(path))
    status, headers, text = _get(url, tok)
    if status == 200:
        try:
            data = json.loads(text)
        except ValueError:
            return {"error": "unreadable answer"}
        if not data:
            return {"error": "no commit for this path"}
        commit = data[0].get("commit") or {}
        when = (commit.get("committer") or {}).get("date") or (commit.get("author") or {}).get("date")
        return {"date": (when or "")[:10], "sha": (data[0].get("sha") or "")[:10],
                "repo": repo, "path": path}
    if status == 404:
        return {"error": "not found in %s" % repo}
    if status in (403, 429):
        remaining = headers.get("X-RateLimit-Remaining")
        reset = headers.get("X-RateLimit-Reset")
        return {"error": "rate limited (remaining=%s)" % remaining,
                "retry_after": reset}
    return {"error": "http %s" % status}


def site_post_date(strategy_id):
    """The WordPress date of the site's own copy, matched by slug."""
    url = ("%s/wp-json/wp/v2/posts?search=%s&_fields=id,date,slug&per_page=5"
           % (SITE, urllib.parse.quote(strategy_id)))
    status, _headers, text = _get(url)
    if status != 200:
        return {"error": "site answered %s" % status}
    try:
        posts = json.loads(text)
    except ValueError:
        return {"error": "unreadable answer"}
    wanted = strategy_id.lower()
    for post in posts:
        if (post.get("slug") or "").lower() == wanted:
            return {"date": (post.get("date") or "")[:10], "slug": post["slug"]}
    return {"error": "no post with this slug"}


def page_strategies(profiles):
    """The strategies the ideas page shows: every member of every family in it.

    This is the set a date column can actually be read from, so it is the set a
    rate-limited run should spend its budget on first.
    """
    if not os.path.exists(IDEAS):
        return []
    ideas = json.load(io.open(IDEAS, encoding="utf-8"))
    ids = []
    for family in ideas.get("families") or []:
        ids.extend(family_members(family, profiles))
        read_from = (family.get("read_from") or {}).get("strategy_id")
        if read_from:
            ids.append(read_from)
    return sorted({i for i in ids if i in profiles})


def load_store():
    if os.path.exists(STORE):
        return json.load(io.open(STORE, encoding="utf-8"))
    return {"schema_version": 1, "strategies": {}}


def write_store(store):
    store["written_by"] = "tools/source_dates.py"
    store["what_this_is"] = (
        "Real dates per strategy from three sources, with the source named: a date the file "
        "name carries (name), the published site's post date (site), and the last commit that "
        "touched the file in the repository it was harvested from (upstream). None of them is "
        "a publication date of the author's revision except where it says so. One writer: "
        "tools/source_dates.py; an emptiness is never filled in by guessing.")
    store["methods"] = {
        "name": "read from the strategy_id (a date, or a Unix timestamp, as written)",
        "site": "WordPress REST of the published site, post slug == strategy_id",
        "upstream": "GitHub API, /repos/{repo}/commits?path={original_file inside the repo}",
        "bulk_import": ("a repository whose checked files share one commit date is an import "
                        "rather than a history; the date is kept and labelled"),
    }
    store["repos"] = repo_kinds(store.get("strategies") or {})
    with io.open(STORE, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(store, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")


def repo_kinds(records):
    """Per repository: how many files were checked, how many dates they carry."""
    seen = {}
    for record in records.values():
        upstream = record.get("upstream") or {}
        repo = upstream.get("repo")
        if not repo or not upstream.get("date"):
            continue
        entry = seen.setdefault(repo, {"checked": 0, "dates": {}})
        entry["checked"] += 1
        date = upstream["date"]
        entry["dates"][date] = entry["dates"].get(date, 0) + 1
    for repo, entry in seen.items():
        entry["distinct_dates"] = len(entry["dates"])
        entry["bulk_import"] = (entry["distinct_dates"] == 1
                                and entry["checked"] >= BULK_MIN_FILES)
    return seen


def fetch(profiles, store, kinds, limit, tok, only=None):
    """Fill in what is missing, stop at the rate limit, and say what happened."""
    records = store.setdefault("strategies", {})
    ids = sorted(only or profiles)
    calls = 0
    added = {"name": 0, "site": 0, "upstream": 0}
    failed = 0
    for strategy_id in ids:
        row = profiles[strategy_id]
        record = records.setdefault(strategy_id, {})
        record.setdefault("repo", row.get("repo") or "")
        if "name" in kinds and not record.get("name_date"):
            value = date_in_name(strategy_id)
            if value:
                record["name_date"] = value
                added["name"] += 1
        if "site" in kinds and (row.get("repo") or "") == "frequenthippo" \
                and "site" not in record:
            record["site"] = site_post_date(strategy_id)
            if record["site"].get("date"):
                added["site"] += 1
        if "upstream" in kinds and "upstream" not in record:
            if limit and calls >= limit:
                print("stopped at the limit of %d API calls; %d strategies of this run are "
                      "untouched" % (limit, len(ids) - ids.index(strategy_id)))
                break
            answer = github_commit(row.get("repo"), upstream_path(row), tok)
            calls += 1
            if answer.get("retry_after") or answer.get("error", "").startswith("rate limited"):
                print("rate limit reached after %d calls; %s"
                      % (calls, answer.get("error")))
                if answer.get("retry_after"):
                    when = time.strftime("%Y-%m-%d %H:%M",
                                         time.localtime(int(answer["retry_after"])))
                    print("the limit resets at %s" % when)
                break
            record["upstream"] = answer
            if answer.get("date"):
                added["upstream"] += 1
            else:
                failed += 1
            if calls % 25 == 0:
                print("  %d calls, %d repositories touched" % (calls, len(repo_kinds(records))))
        record["fetched_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    return {"calls": calls, "added": added, "failed": failed}


def summary(store):
    records = store.get("strategies") or {}
    kinds = {"name": 0, "site": 0, "upstream": 0}
    for record in records.values():
        if record.get("name_date"):
            kinds["name"] += 1
        if (record.get("site") or {}).get("date"):
            kinds["site"] += 1
        if (record.get("upstream") or {}).get("date"):
            kinds["upstream"] += 1
    repos = repo_kinds(records)
    bulk = sorted(repo for repo, entry in repos.items() if entry["bulk_import"])
    print("strategies with a date : name %d, site %d, upstream %d (of %d recorded)"
          % (kinds["name"], kinds["site"], kinds["upstream"], len(records)))
    print("repositories checked   : %d, of which one import date: %d"
          % (len(repos), len(bulk)))
    for repo in bulk[:10]:
        entry = repos[repo]
        print("  import: %-34s %d files, %s"
              % (repo, entry["checked"], ", ".join(sorted(entry["dates"]))))
    return kinds, repos


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Record real dates per strategy from the name, the site and the source repo.")
    parser.add_argument("--fetch", action="store_true", help="fill in missing dates")
    parser.add_argument("--kinds", default="name,site,upstream",
                        help="which dates to fetch (default all three)")
    parser.add_argument("--limit", type=int, default=0,
                        help="stop after this many GitHub API calls (0 = no limit)")
    parser.add_argument("--strategies", default="",
                        help="comma-separated strategy_ids (default: the whole corpus)")
    parser.add_argument("--only-missing", action="store_true",
                        help="skip strategies that already have an upstream date")
    parser.add_argument("--on-page", action="store_true",
                        help="restrict to the strategies the ideas page shows")
    parser.add_argument("--summary", action="store_true", help="print coverage and exit")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()

    profiles = load_profiles()
    store = load_store()
    if args.summary:
        summary(store)
        return 0
    if not args.fetch:
        parser.print_help()
        return 0

    kinds = [k.strip() for k in args.kinds.split(",") if k.strip()]
    wanted = [s.strip() for s in args.strategies.split(",") if s.strip()] or None
    if args.on_page:
        on_page = page_strategies(profiles)
        print("strategies on the ideas page: %d" % len(on_page))
        wanted = [s for s in on_page if not wanted or s in wanted]
    if args.only_missing:
        wanted = [s for s in (wanted or sorted(profiles))
                  if not (store.get("strategies", {}).get(s) or {}).get("upstream")]
    tok = token()
    print("token: %s" % ("found in the environment or user_data/.github_token" if tok
                         else "none - 60 requests an hour, which is not enough for a corpus"))
    limit = rate_limit(tok)
    if limit:
        print("github api: %s requests an hour, %s left"
              % (limit.get("limit"), limit.get("remaining")))
    if "site" in kinds:
        # The site is not rate limited, so its own files are done in one pass and
        # only those files - the site also publishes pages about harvested
        # strategies, and those dates would be ours, not the author's.
        print("files taken from the site: %d"
              % len([s for s in profiles if (profiles[s].get("repo") or "") == "frequenthippo"]))
    result = fetch(profiles, store, kinds, args.limit, tok, wanted)
    write_store(store)
    print("fetched: %d API calls, name %d, site %d, upstream %d, without a date %d"
          % (result["calls"], result["added"]["name"], result["added"]["site"],
             result["added"]["upstream"], result["failed"]))
    summary(store)
    return 0


def selftest():
    cases = 0
    assert date_in_name("E0V1E_20230915") == "2023-09-15"
    assert date_in_name("E0V1E_20231014_0847") == "2023-10-14"
    assert date_in_name("GeneTrader_gen9_1735161895_5455") == "2024-12-25"
    assert date_in_name("ZaratustraV31") == ""
    cases += 4
    assert upstream_path({"original_file": "repos/a_b/strategies/X.py", "repo": "a/b"}) == \
        "strategies/X.py"
    assert upstream_path({"original_file": "user_data/x.py", "repo": "a/b"}) == ""
    cases += 2
    kinds = repo_kinds({
        "A": {"upstream": {"repo": "m/n", "date": "2025-09-10"}},
        "B": {"upstream": {"repo": "m/n", "date": "2025-09-10"}},
        "C": {"upstream": {"repo": "m/n", "date": "2025-09-10"}},
        "D": {"upstream": {"repo": "m/n", "date": "2025-09-10"}},
        "E": {"upstream": {"repo": "m/n", "date": "2025-09-10"}},
        "F": {"upstream": {"repo": "o/p", "date": "2021-10-12"}},
        "G": {"upstream": {"repo": "o/p", "date": "2023-05-01"}},
    })
    assert kinds["m/n"]["bulk_import"] is True and kinds["o/p"]["bulk_import"] is False, kinds
    cases += 1
    print("source_dates selftest: PASS (%d cases)" % cases)
    return 0


if __name__ == "__main__":
    sys.exit(main())
