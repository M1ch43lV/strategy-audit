"""Merge disjoint identity-bound bias shards into the canonical evidence file."""
from __future__ import annotations

import argparse
import io
import json
import os

import profile_bias


def _load(path):
    with io.open(path, encoding="utf-8") as handle:
        return json.load(handle)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=profile_bias.OUTPUT)
    parser.add_argument("--input", action="append", required=True)
    args = parser.parse_args(argv)
    profiles = {row["strategy_id"]: row for row in profile_bias._csv(profile_bias.PROFILES)}
    target = profile_bias._load(args.target)
    merged = 0
    for path in args.input:
        shard = _load(path)
        for strategy, record in (shard.get("results") or {}).items():
            if strategy not in profiles or not profile_bias.identity_matches(profiles[strategy], record):
                raise SystemExit("identity mismatch in %s: %s" % (path, strategy))
            existing = target["results"].get(strategy)
            if existing and profile_bias.identity_matches(profiles[strategy], existing):
                for diagnostic in ("lookahead", "recursive"):
                    old = existing.get(diagnostic, {}).get("status")
                    new = record.get(diagnostic, {}).get("status")
                    if old in ("PASS", "FOUND") and new in ("PASS", "FOUND") and old != new:
                        raise SystemExit("conflicting %s result for %s" % (diagnostic, strategy))
            target["results"][strategy] = record
            merged += 1
    profile_bias._write(target, args.target)
    print("merged %d shard records; canonical records %d" %
          (merged, len(target["results"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
