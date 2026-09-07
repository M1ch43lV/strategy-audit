# -*- coding: utf-8 -*-
"""Refresh `graphify-scope/` from the live tree before rebuilding the graph.

`graphify-scope/` is a hand-curated *copy* of the audit machinery - the root
scripts, `regime/`, `repair/`, `tools/`, `cluster/` and the current `.md`
documents - deliberately excluding `repos/`, `ftenv/`, `old/`, `corpus/`,
`user_data/` and `repair/patched/`, which would otherwise bury 130 relevant
files under several hundred thousand irrelevant ones.

Being a copy, it goes stale silently: on 2026-09-07 the graph was rebuilt
from a `regime/full_backtest.py` that was a day old, and nothing said so.
This script only refreshes what the curation already chose - it copies the
live version of every file already present in the copy and never adds new
paths, so the curation decision stays where it was made rather than drifting
with whatever happens to sit in the tree.
"""
from __future__ import annotations

import filecmp
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCOPE = ROOT / "graphify-scope"


def sync() -> tuple[list[str], list[str], int]:
    refreshed, orphaned, unchanged = [], [], 0
    for copied in SCOPE.rglob("*"):
        if not copied.is_file():
            continue
        relative = copied.relative_to(SCOPE)
        # The scan copy has its own graphify-out/ from an earlier build; it is
        # build output, not build input, and has no live counterpart.
        if relative.parts and relative.parts[0] == "graphify-out":
            continue
        live = ROOT / relative
        if not live.is_file():
            orphaned.append(str(relative))
        elif filecmp.cmp(live, copied, shallow=False):
            unchanged += 1
        else:
            shutil.copy2(live, copied)
            refreshed.append(str(relative))
    return refreshed, orphaned, unchanged


def main() -> int:
    refreshed, orphaned, unchanged = sync()
    for name in sorted(refreshed):
        print("refreshed", name)
    for name in sorted(orphaned):
        print("no longer in live tree:", name)
    print(f"{len(refreshed)} refreshed, {unchanged} unchanged, {len(orphaned)} orphaned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
