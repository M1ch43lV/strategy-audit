# -*- coding: utf-8 -*-
"""strategy_families - families of strategies, with similar name stems merged.

A family needs at least two strategies. `tools.strategy_ideas.family_stem()` is
the mechanical guess (name without its version marker); it splits
`BB_RPB_TSL` from `BB_RPB_TSL_RNG` although they are one line of work. This
module merges two stems only when BOTH hold:

1. one stem is a token prefix of the other (`bb_rpb_tsl` of `bb_rpb_tsl_rng`) or
   they are equal ignoring case and separators (`bbrsi`, `BBRSI`), and
2. the code is similar: the best Jaccard similarity of 5-token shingles between
   up to ``SAMPLE`` files of each stem (spread over its sorted members, so a
   stem's odd one out does not decide alone) is at least ``MIN_SIMILARITY``.

The name only proposes a merge, the code decides it, so `Supertrend` does not
swallow `SupertrendScalperXYZ` just because it is shorter. Every merge records
its similarity and the pair it was decided on, so a wrong merge can be refuted
on the individual case. Nothing here is a measurement.

Usage:
    python -m tools.strategy_families --summary
    python -m tools.strategy_families --show BB_RPB_TSL
    python -m tools.strategy_families --write      # evidence/STRATEGY_FAMILIES.json
"""
from __future__ import annotations

import argparse
import io
import json
import keyword
import os
import re
import sys

_ROOT = (os.environ.get("AUDIT_ROOT") or
         os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from tools import strategy_ideas as si  # noqa: E402

OUTPUT = os.path.join(_ROOT, "evidence", "STRATEGY_FAMILIES.json")
MIN_SIMILARITY = 0.5
SHINGLE = 5
SAMPLE = 12
TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+\.?\d*")
KEYWORDS = set(keyword.kwlist)


def name_tokens(stem: str) -> list[str]:
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", stem)
    return [t for t in re.split(r"[_\-\s]+", spaced.lower()) if t]


def is_prefix_pair(short: str, long: str) -> bool:
    a, b = name_tokens(short), name_tokens(long)
    if "".join(a) == "".join(b):
        return True
    return len(a) < len(b) and b[:len(a)] == a and len(short) >= 4


def shingles(path: str) -> set:
    try:
        with io.open(path, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
    except OSError:
        return set()
    text = re.sub(r"#.*", "", text)
    tokens = [t for t in TOKEN.findall(text) if t not in KEYWORDS]
    return {tuple(tokens[i:i + SHINGLE]) for i in range(max(0, len(tokens) - SHINGLE + 1))}


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def build(profiles=None, classification=None) -> dict:
    profiles = profiles if profiles is not None else si.load_profiles()
    classification = classification if classification is not None else si.load_classification()
    groups: dict[str, list[str]] = {}
    for strategy_id in profiles:
        stem = si.family_stem(strategy_id)
        if stem in si.TEMPLATE_STEMS:
            continue
        if (classification.get(strategy_id) or {}).get("strategy_type") == "not_applicable":
            continue
        groups.setdefault(stem, []).append(strategy_id)
    for members in groups.values():
        members.sort()

    def sample(members):
        if len(members) <= SAMPLE:
            return members
        step = (len(members) - 1) / (SAMPLE - 1)
        return [members[round(i * step)] for i in range(SAMPLE)]

    fingerprints: dict[str, set] = {}

    def fingerprint(sid):
        if sid not in fingerprints:
            path = os.path.join(_ROOT, profiles[sid]["canonical_file"].replace("/", os.sep))
            fingerprints[sid] = shingles(path)
        return fingerprints[sid]

    def similarity_of(short, long):
        best, pair = 0.0, None
        for a in sample(groups[short]):
            for b in sample(groups[long]):
                value = jaccard(fingerprint(a), fingerprint(b))
                if value > best:
                    best, pair = value, [a, b]
        return best, pair

    parent = {stem: stem for stem in groups}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    by_first: dict[str, list[str]] = {}
    for stem in groups:
        by_first.setdefault((name_tokens(stem) or [""])[0], []).append(stem)

    merges = []
    for stems in by_first.values():
        stems = sorted(stems, key=lambda s: (len(name_tokens(s)), s))
        for i, short in enumerate(stems):
            for long in stems[i + 1:]:
                if find(short) == find(long) or not is_prefix_pair(short, long):
                    continue
                similarity, pair = similarity_of(short, long)
                if similarity >= MIN_SIMILARITY:
                    parent[find(long)] = find(short)
                    merges.append({"stem": long, "into": short, "similarity": round(similarity, 3),
                                   "decided_on": pair})

    families: dict[str, list[str]] = {}
    for stem, members in groups.items():
        families.setdefault(find(stem), []).extend(members)
    result = []
    for root, members in sorted(families.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        members.sort()
        stems = sorted({si.family_stem(m) for m in members})
        result.append({"family": root, "size": len(members), "stems": stems, "members": members})
    return {"min_similarity": MIN_SIMILARITY, "shingle": SHINGLE,
            "families": result, "merges": merges}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--show", default="", help="print the family whose name or stem matches")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    data = build()
    families = data["families"]
    multi = [f for f in families if f["size"] >= 2]
    if args.summary or not (args.show or args.write):
        print("%d groups by stem before merging, %d families after merging, %d with 2+ strategies "
              "(%d strategies), %d singletons, %d merges" % (
                  len({s for f in families for s in f["stems"]}), len(families), len(multi),
                  sum(f["size"] for f in multi), len(families) - len(multi), len(data["merges"])))
    if args.show:
        needle = args.show.lower()
        for family in families:
            if needle == family["family"].lower() or needle in [s.lower() for s in family["stems"]]:
                print(json.dumps(family, indent=1))
                for merge in data["merges"]:
                    if merge["into"] in family["stems"] or merge["stem"] in family["stems"]:
                        print("  merge:", merge)
    if args.write:
        with io.open(OUTPUT, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=1)
        print("wrote", os.path.relpath(OUTPUT, _ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
