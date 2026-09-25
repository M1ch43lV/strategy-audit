# -*- coding: utf-8 -*-
"""label_runner - label batches of strategy sheets with headless `claude -p --model haiku`.

Reads evidence/labels_full/batch_NNN.json, writes result_NNN.json. Only strategies still
missing from a result are sent again (up to PASSES passes), so an incomplete answer is
completed instead of replaced.

    python -m tools.label_runner 29 108 [--workers 6]
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(_ROOT, "evidence", "labels_full")
RULES = os.path.join(_ROOT, "tools", "strategy_labels_prompt.txt")
PASSES = 3


def ask(rows: list[dict]) -> list[dict]:
    rules = io.open(RULES, encoding="utf-8").read()
    prompt = (rules + "\n\nLabel every strategy below. Answer with the JSON array only, one object per "
              "strategy, no prose, no code fence.\n\n" + json.dumps(rows, ensure_ascii=False))
    out = subprocess.run(["claude", "-p", "--model", "haiku"], input=prompt, capture_output=True,
                         text=True, encoding="utf-8", timeout=900).stdout
    start, end = out.find("["), out.rfind("]")
    if start < 0 or end < start:
        return []
    try:
        return [e for e in json.loads(out[start:end + 1]) if isinstance(e, dict)]
    except ValueError:
        return []


def run(number: int) -> str:
    tag = "%03d" % number
    batch_path = os.path.join(WORK, "batch_%s.json" % tag)
    result_path = os.path.join(WORK, "result_%s.json" % tag)
    rows = json.load(io.open(batch_path, encoding="utf-8"))
    have: dict[str, dict] = {}
    if os.path.exists(result_path):
        try:
            have = {e["id"]: e for e in json.load(io.open(result_path, encoding="utf-8"))}
        except ValueError:
            have = {}
    for _ in range(PASSES):
        todo = [r for r in rows if r["id"] not in have]
        if not todo:
            break
        wanted = {r["id"] for r in todo}
        for entry in ask(todo):
            if entry.get("id") in wanted:
                have[entry["id"]] = entry
        with io.open(result_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump([have[r["id"]] for r in rows if r["id"] in have], handle, ensure_ascii=False, indent=1)
    return "%s %d/%d" % (tag, len(have), len(rows))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("first", type=int)
    parser.add_argument("last", type=int)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    with ThreadPoolExecutor(args.workers) as pool:
        for line in pool.map(run, range(args.first, args.last + 1)):
            print(line, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
