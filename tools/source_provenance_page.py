# -*- coding: utf-8 -*-
"""source_provenance_page - rewrite saved_resource.html (Strategy provenance) from the evidence tables.

Inputs: evidence/corpus_sources.json (tools.census_repos), evidence/EXECUTION_PROFILES.csv and
evidence/REGIME_ELIGIBILITY.csv. Everything up to <body> (styles, fonts) is kept from the existing
page; only the head texts and the body are rewritten.

    python -m tools.source_provenance_page
"""
from __future__ import annotations

import csv
import html
import io
import json
import os
import re
import sys

_ROOT = (os.environ.get("AUDIT_ROOT") or
         os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)

PAGE = os.path.join(_ROOT, "saved_resource.html")
SOURCES = os.path.join(_ROOT, "evidence", "corpus_sources.json")
PROFILES = os.path.join(_ROOT, "evidence", "EXECUTION_PROFILES.csv")
ELIGIBILITY = os.path.join(_ROOT, "evidence", "REGIME_ELIGIBILITY.csv")


def _link(repo: str) -> str:
    return ('<a href="https://github.com/%s" target="_blank" rel="noopener">%s</a>'
            % (html.escape(repo), html.escape(repo)))


def _rows(path):
    with io.open(path, encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def collect() -> dict:
    sources = json.load(io.open(SOURCES, encoding="utf-8"))
    repo_of, files = {}, {}
    for row in _rows(PROFILES):
        repo_of[row["strategy_id"]] = row["repo"]
        files.setdefault(row["repo"], set()).add(row["strategy_id"])
    eligible = {}
    for row in _rows(ELIGIBILITY):
        if row["regime_eligible"] == "true":
            eligible.setdefault(repo_of.get(row["strategy_id"], "?"), set()).add(row["strategy_id"])
    repos = []
    for entry in sources["repos"]:
        name = entry["repo"]
        repos.append({"repo": name, "found": entry["classes"], "unique": entry["first"],
                      "files": len(files.get(name, ())), "eligible": len(eligible.get(name, ()))})
    repos.sort(key=lambda r: (-r["unique"], -r["found"], r["repo"]))
    return {"repos": repos, "eligible_total": sum(len(v) for v in eligible.values()),
            "occurrences": sources["occurrences"], "unique": sources["unique"]}


def _row(r, top) -> str:
    zero = r["unique"] == 0
    width = round(100.0 * r["unique"] / top, 2) if top else 0
    dash = '<span class="nil">&mdash;</span>'
    return ('<tr%s><td class="repo">%s</td><td class="num">%d</td><td class="num">%d</td>'
            '<td class="barcell"><span class="bar" style="width:%s%%"></span></td>'
            '<td class="num">%s</td><td class="num">%s</td></tr>'
            % (' class="zero"' if zero else "", _link(r["repo"]), r["found"], r["unique"], width,
               r["files"] or "&mdash;",
               '<span class="yield">%d</span>' % r["eligible"] if r["eligible"] else dash))


def body(data) -> str:
    repos = data["repos"]
    top = max(r["unique"] for r in repos)
    copies = [r for r in repos if r["unique"] == 0 and r["found"] > 0]
    empty = [r for r in repos if r["found"] == 0]
    contributing = sum(1 for r in repos if r["unique"] > 0)
    biggest = max(copies, key=lambda r: r["found"]) if copies else None
    joined = " &middot; ".join
    parts = ['''<body>
<div class="wrap">
  <header>
    <div class="eyebrow">Sources of the strategy corpus</div>
    <h1>Strategy provenance</h1>
    <p class="lede">Every GitHub repository the Freqtrade strategies of this audit come from &mdash; and what each one actually contributed.</p>
  </header>
''']
    parts.append('''  <div class="stats">
    <div class="stat"><b>{n}</b><span>repositories</span></div>
    <div class="stat"><b>{occ:,}</b><span>classes found</span></div>
    <div class="stat"><b>{uni:,}</b><span>of which unique</span></div>
    <div class="stat"><b>{elig}</b><span>currently eligible</span></div>
  </div>
'''.format(n=len(repos), occ=data["occurrences"], uni=data["unique"], elig=data["eligible_total"]))
    parts.append('''  <section>
    <h2>What the numbers mean</h2>
    <p>The {n} repositories hold {occ:,} strategy classes, but only <strong>{uni:,}</strong> of them are distinct. The rest are copies: the same strategy turns up in several collections, often unchanged. <em>Unique</em> counts how many strategies are credited to a repository as their first place of discovery &mdash; that is its real contribution.</p>
    <p class="note">The last column shows how many of a repository&rsquo;s strategies have passed the checks so far. The number is strict: it requires a valid measurement, clean coverage and both bias checks. It is still growing while the expansion waves are worked through.</p>
  </section>
'''.format(n=len(repos), occ=data["occurrences"], uni=data["unique"]))
    parts.append('''  <section>
    <h2>The {n} sources</h2>
    <div class="scroller">
      <table>
        <thead>
          <tr>
            <th>Repository</th>
            <th class="n">found</th>
            <th class="n">unique</th>
            <th></th>
            <th class="n">files</th>
            <th class="n">eligible</th>
          </tr>
        </thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </div>
    <p class="note">Sorted by unique contribution. Highlighted rows contributed not a single strategy that had not already been found elsewhere.</p>
  </section>
'''.format(n=len(repos), rows="\n".join("          " + _row(r, top) for r in repos)))
    if copies:
        example = (" The largest example is <code>%s</code> with %d classes and not a single first find."
                   % (html.escape(biggest["repo"]), biggest["found"]))
        parts.append('''  <section>
    <h2>Collections with no contribution of their own</h2>
    <div class="callout">
      <h3>{n} repositories contain nothing but copies</h3>
      <p class="note">They are not worthless &mdash; they show how widely individual strategies are spread. For the analysis they do not count as independent observations, though; otherwise a much-copied strategy would multiply its own result.{ex}</p>
      <div class="repolist">{lst}</div>
    </div>
  </section>
'''.format(n=len(copies), ex=example, lst=joined(_link(r["repo"]) for r in copies)))
    if empty:
        parts.append('''  <section>
    <h2>Without usable strategy classes</h2>
    <p class="note">{n} repositories were downloaded but held no strategy class in the corpus&rsquo;s sense &mdash; tools and side projects rather than trading logic.</p>
    <div class="repolist">{lst}</div>
  </section>
'''.format(n=len(empty), lst=joined(_link(r["repo"]) for r in empty)))
    parts.append('''  <footer>
    Compiled from <code>corpus_sources.json</code>, <code>EXECUTION_PROFILES.csv</code> and <code>REGIME_ELIGIBILITY.csv</code> of the audit. {c} of the {n} repositories yield at least one unique strategy.
  </footer>
</div>
</body>
</html>
'''.format(c=contributing, n=len(repos)))
    return "".join(parts)


def main() -> int:
    page = io.open(PAGE, encoding="utf-8").read()
    head = page[:page.index("<body>")]
    head = head.replace('<html lang="de">', '<html lang="en">')
    head = re.sub(r'(<meta name="description" content=")[^"]*"',
                  r'\1Every GitHub repository the Freqtrade strategies of the audit come from, with what each actually contributed."',
                  head)
    head = re.sub(r"<title>.*?</title>", "<title>Strategy provenance</title>", head)
    data = collect()
    io.open(PAGE, "w", encoding="utf-8", newline="\n").write(head + body(data))
    print("%d repositories, %d unique classes, %d eligible -> %s"
          % (len(data["repos"]), data["unique"], data["eligible_total"], os.path.relpath(PAGE, _ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
