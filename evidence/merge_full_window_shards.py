# -*- coding: utf-8 -*-
"""Merge the sharded full-window containers' own output files into the one
store `evidence/strategy_status.py` reads.

Three containers wrote to three separate files - `evidence/PROFILE_FULL_WINDOW.json`
itself is a single JSON document with no cross-process lock, and two
processes loading it, updating their own slice, and writing back would race:
whichever finished last would overwrite the other's results with the copy it
loaded before the first one's writes existed. Separate files per shard sidesteps
the race entirely; this script is the one writer to the shared file, and it
only ever runs after the shards, never alongside them.

Safe to re-run at any time while the shard containers are still working -
each strategy's record is only added or replaced, nothing already merged is
ever removed, so an in-progress shard file merges whatever it has finished
so far without disturbing the rest.
"""
import io
import json
import os


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "evidence/PROFILE_FULL_WINDOW.json")
SHARDS = ("evidence/PROFILE_FULL_WINDOW_shardA.json", "evidence/PROFILE_FULL_WINDOW_shardB.json",
         "evidence/PROFILE_FULL_WINDOW_shardTF.json")


def _load(path):
    if not os.path.exists(path):
        return None
    return json.load(io.open(path, encoding="utf-8"))


def merge():
    target = _load(TARGET) or {"schema_version": 1, "results": {}}
    added, updated = 0, 0
    pair_universes = dict(target.get("pair_universes") or {})
    for shard_name in SHARDS:
        shard = _load(os.path.join(ROOT, shard_name))
        if not shard:
            continue
        pair_universes.update(shard.get("pair_universes") or {})
        for strategy, record in shard.get("results", {}).items():
            previous = target["results"].get(strategy)
            if previous == record:
                continue
            target["results"][strategy] = record
            if previous is None:
                added += 1
            else:
                updated += 1
    target["pair_universes"] = pair_universes
    # `timerange` is per-mode in every shard and identical by construction
    # (profile_full_window.TIMERANGE is a module constant); take the first
    # shard's value rather than inventing a merged one.
    for shard_name in SHARDS:
        shard = _load(os.path.join(ROOT, shard_name))
        if shard and shard.get("timerange"):
            target["timerange"] = shard["timerange"]
            break
    tmp = TARGET + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(target, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, TARGET)
    measured = sum(1 for r in target["results"].values()
                   if r.get("status") == "measured")
    print("merged: %d new, %d updated, %d total rows, %d measured"
          % (added, updated, len(target["results"]), measured))
    return added, updated


if __name__ == "__main__":
    merge()
