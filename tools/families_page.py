# -*- coding: utf-8 -*-
"""families_page - data for the Strategy Ideas page: every family with 2+ strategies, with labels.

Families come from `tools.strategy_families` (similar name stems merged, a family needs at
least two strategies). Logic labels come from `evidence/STRATEGY_LABELS.json`
(`tools.strategy_labels`): a family carries a label when more than half of its members do.
The written descriptions in `evidence/STRATEGY_IDEAS.json` belong to a family stem; each is
attached to the family that stem now belongs to, so a family without a description says so.

    python -m tools.families_page              # writes strategy_ideas_data.json
"""
from __future__ import annotations

import html
import io
import json
import os
import sys

_ROOT = (os.environ.get("AUDIT_ROOT") or
         os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)

from tools import strategy_families as sf  # noqa: E402
from tools import strategy_ideas as si  # noqa: E402
from tools import strategy_labels as sl  # noqa: E402

OUTPUT = os.path.join(_ROOT, "strategy_ideas_data.json")
IDEAS = os.path.join(_ROOT, "evidence", "STRATEGY_IDEAS.json")
PAGE_DATA = os.path.join(_ROOT, "artifact_index_data.json")


def _members_rows(members, profiles, store):
    rows = []
    for sid in members:
        entry = store["strategies"].get(sid) or {}
        labels = sorted(l["label"] for l in entry.get("labels", []) if l["confidence"] != "low")
        facts = entry.get("facts") or {}
        tags = [k for k in ("scalper", "futures_capable", "dca", "ml_ai") if facts.get(k)]
        profile = profiles.get(sid) or {}
        rows.append(["<code>%s</code>" % html.escape(sid), entry.get("primary") or "-",
                     ", ".join(labels) or "-", ", ".join(tags) or "-",
                     facts.get("timeframe") or profile.get("execution_timeframe") or "-",
                     html.escape(profile.get("canonical_file", ""))])
    return rows


def build() -> dict:
    families = json.load(io.open(sf.OUTPUT, encoding="utf-8"))
    store = json.load(io.open(sl.FULL_STORE, encoding="utf-8"))
    profiles = si.load_profiles()
    described = {f["name"]: f for f in json.load(io.open(PAGE_DATA, encoding="utf-8"))["families"]}
    labels_by_family = {f["family"]: f for f in sl.family_labels(store, families)}
    out = []
    for fam in families["families"]:
        if fam["size"] < 2:
            continue
        info = labels_by_family.get(fam["family"], {})
        ideas = [described[s] for s in fam["stems"] if s in described]
        ideas.sort(key=lambda d: -int(d["count"]))
        item = {
            "name": fam["family"], "count": fam["size"], "stems": fam["stems"],
            "labels": info.get("labels", []), "variant_labels": info.get("variant_labels", {}),
            "idea_html": "", "version_headers": [], "version_rows": [], "read_from_html": "",
            "details_items": [],
            "file_headers": ["Strategy", "Primary", "Labels", "Facts", "Timeframe", "File"],
            "file_rows": _members_rows(fam["members"], profiles, store),
        }
        if ideas:
            main = ideas[0]
            item["idea_html"] = main["idea_html"]
            item["version_headers"] = main.get("version_headers", [])
            item["version_rows"] = main.get("version_rows", [])
            item["read_from_html"] = main.get("read_from_html", "")
            item["details_items"] = main.get("details_items", [])
            item["described_stem"] = main["name"]
            if len(ideas) > 1:
                item["other_descriptions"] = [{"stem": d["name"], "idea_html": d["idea_html"]} for d in ideas[1:]]
        out.append(item)
    intro = json.load(io.open(PAGE_DATA, encoding="utf-8"))["intro_paras"]
    intro = intro[:1] + [
        "<strong>Families and labels.</strong> A family is two or more strategies whose names share a stem "
        "and whose code is similar (similar stems such as <code>BB_RPB_TSL</code> and "
        "<code>BB_RPB_TSL_RNG</code> are merged); a strategy without a sibling is not a family. Labels are read "
        "from the entry and exit code by Haiku 4.5, each with a verbatim code snippet as evidence "
        "(<code>evidence/STRATEGY_LABELS.json</code>). A family carries a label when more than half of its "
        "members do; other labels show as <em>variants</em>. Labels describe the logic, not its quality, "
        "and a family without a written description shows its members only."]
    return {"intro_paras": intro, "families": out,
            "labels": list(sl.LABELS), "prompt_sha256": store.get("prompt_sha256"), "model": store.get("model")}


def main() -> int:
    if not os.path.exists(PAGE_DATA):
        # first run: keep the hand-written descriptions the page had before this builder
        import shutil
        shutil.copyfile(OUTPUT, PAGE_DATA)
    data = build()
    with io.open(OUTPUT, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, separators=(",", ":"))
    print("%d families, %d strategies -> %s" % (len(data["families"]),
          sum(f["count"] for f in data["families"]), os.path.relpath(OUTPUT, _ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
