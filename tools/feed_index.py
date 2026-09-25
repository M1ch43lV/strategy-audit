# -*- coding: utf-8 -*-
"""Build a searchable index of the whole FrequentHippo strategy feed.

Reads only public post metadata from the WordPress REST API (category 8, 100
posts per request) and writes ``evidence/feed_index/data.json`` plus the
static page ``evidence/feed_index/index.html``. Nothing is written under
``repos/`` and no strategy file is downloaded; the index is a lead list, the
same boundary ``evidence.strategy_feed`` draws.

Record layout (JSON array): [post_id, date, title, "owner/repo", commit,
path_in_repo, site_upload_name, flags]. flags bit 1 = the repository is
already harvested under ``repos/``, bit 2 = the file stem matches one of the
dashboard top-10 leads in ``LEADS``, bit 4 = no strategy of that name
is in the corpus (``STRATEGY_STATUS.csv``: strategy_id or source file stem;
a name match, not a content match), bit 8 = our own post (repository
M1ch43lV/strategy-audit), which is in the corpus by definition and never
carries bit 4, bit 16 = the file exists at that path under ``repos/``.
"""
from __future__ import annotations

import csv
import json
import os
import re
import time
from urllib.parse import unquote
from datetime import datetime, timezone
from urllib.request import Request, urlopen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "evidence", "feed_index")
POSTS = ("https://frequenthippo.ddns.net/wp-json/wp/v2/posts"
         "?categories=8&per_page=100&_fields=id,date,title,content&page=")
UA = {"User-Agent": "strategy-audit-stage0/1.0 (+https://github.com/M1ch43lV/strategy-audit)"}
RAW = re.compile(r"https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/([^'\"<]+)")
UPLOAD = re.compile(r"/wp-content/uploads/strategies/([^'\"<]+\.py)")
OWN = "M1ch43lV/strategy-audit"
LEADS = ("BinHModWhiteHOV0", "CombinedBinHClucAndSMAOffset", "BB_RPB_TSL_RNG",
         "BB_RPB_TSL_jilv220", "Combined_NFIv7_SMA_Rallipanos",
         "CombinedBinHClucAndMADV3", "BinClucMad", "ElliotV2")


def fetch_all() -> list[list]:
    rows, page = [], 1
    while True:
        for attempt in range(4):
            try:
                with urlopen(Request(POSTS + str(page), headers=UA), timeout=90) as r:
                    batch = json.load(r)
                break
            except Exception as exc:
                if getattr(exc, "code", 0) == 400:
                    batch = []
                    break
                time.sleep(3)
        else:
            raise SystemExit(f"page {page} failed")
        if not batch:
            return rows
        for p in batch:
            html = p["content"]["rendered"]
            raw, up = RAW.search(html), UPLOAD.search(html)
            title = re.sub(r"<[^>]+>", "", p["title"]["rendered"])
            rows.append([p["id"], p["date"][:10], title,
                         f"{raw.group(1)}/{raw.group(2)}" if raw else "",
                         raw.group(3) if raw else "", raw.group(4) if raw else "",
                         up.group(1) if up else ""])
        page += 1
        time.sleep(0.3)


def corpus_names() -> set[str]:
    names: set[str] = set()
    with open(os.path.join(ROOT, "STRATEGY_STATUS.csv"), encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            names.add(row["strategy_id"].lower())
            names.add(os.path.splitext(os.path.basename(row["source_file"]))[0].lower())
    return names


def main() -> None:
    known = corpus_names()
    harvested = {d.lower() for d in os.listdir(os.path.join(ROOT, "repos"))}
    rows = fetch_all()
    for r in rows:
        stem = os.path.splitext(os.path.basename(r[5] or r[6]))[0]
        flag = 1 if r[3].replace("/", "_").lower() in harvested else 0
        flag |= 2 if stem.startswith(LEADS) else 0
        if r[3] and os.path.exists(os.path.join(ROOT, "repos", r[3].replace("/", "_"), unquote(r[5]))):
            flag |= 16
        if r[3] == OWN:
            flag |= 8
        elif stem.lower() not in known:
            flag |= 4
        r.append(flag)
    os.makedirs(OUT, exist_ok=True)
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "rows": rows}
    with open(os.path.join(OUT, "data.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, separators=(",", ":"))
    print(len(rows), "posts")


if __name__ == "__main__":
    main()
