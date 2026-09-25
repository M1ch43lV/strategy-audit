# -*- coding: utf-8 -*-
"""label_check - blind second opinion on a stratified sample of the logic labels.

Draws a sample from evidence/STRATEGY_LABELS.json (fixed quotas per Haiku primary label, seed
fixed), sends the same fact sheets and rules to DeepSeek without the Haiku answer, and compares.
Agreement between two models is not accuracy; the disagreements are what a person reads.

    python -m tools.label_check --draw         # evidence/labels_check/sample.json
    python -m tools.label_check --ask          # evidence/labels_check/deepseek.json
    python -m tools.label_check --compare
"""
from __future__ import annotations

import argparse
import glob
import io
import json
import os
import random
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from tools import strategy_labels as sl  # noqa: E402

DIR = os.path.join(_ROOT, "evidence", "labels_check")
SAMPLE = os.path.join(DIR, "sample.json")
ANSWERS = os.path.join(DIR, "deepseek.json")
MODEL = "deepseek-v4-flash"
QUOTAS = {"mean_reversion": 30, "trend_following": 30, "momentum": 30, "other": 30, "breakout": 20,
          "volatility": 15, "pattern": 15, "statistical": 10, "volume_flow": 10, "grid": 10}
PER_CALL = 10


def draw() -> None:
    store = json.load(io.open(sl.FULL_STORE, encoding="utf-8"))["strategies"]
    sheets = {}
    for path in glob.glob(os.path.join(sl.FULL_WORKDIR, "batch_*.json")):
        for row in json.load(io.open(path, encoding="utf-8")):
            sheets[row["id"]] = row["sheet"]
    rng = random.Random(20260925)
    rows = []
    for label, quota in QUOTAS.items():
        pool = sorted(i for i, e in store.items() if e["primary"] == label)
        rng.shuffle(pool)
        rows += [{"id": i, "sheet": sheets[i], "stratum": label, "stratum_size": len(pool)} for i in pool[:quota]]
    os.makedirs(DIR, exist_ok=True)
    json.dump(rows, io.open(SAMPLE, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    print(len(rows), "sampled ->", os.path.relpath(SAMPLE, _ROOT))


DESCRIBE = ("\n\nEvery object MUST carry the `description` field of the output format: two or three plain "
            "English sentences saying what the strategy does (what triggers the entry, what ends the trade, "
            "timeframe, any notable protection or stoploss idea), written from the fact sheet only. No "
            "quality or profit judgement, no advice.")


def _call(rows):
    """One request: logic classification and a written description for every strategy in `rows`."""
    rules = io.open(sl.PROMPT, encoding="utf-8").read()
    rules = rules.replace('  "note":', '  "description": "<two or three sentences, see below>",\n  "note":', 1) + DESCRIBE
    prompt = (rules + "\n\nLabel and describe every strategy below. Answer with the JSON array only, no prose, no code fence.\n\n"
              + json.dumps([{"id": r["id"], "sheet": r["sheet"]} for r in rows], ensure_ascii=False))
    body = json.dumps({"model": MODEL, "messages": [{"role": "user", "content": prompt}],
                       "temperature": 0}).encode()
    request = urllib.request.Request("https://api.deepseek.com/chat/completions", data=body, headers={
        "Content-Type": "application/json", "Authorization": "Bearer " + os.environ["DEEPSEEK_API_KEY"]})
    with urllib.request.urlopen(request, timeout=600) as response:
        text = json.load(response)["choices"][0]["message"]["content"]
    start, end = text.find("["), text.rfind("]")
    try:
        return [e for e in json.loads(text[start:end + 1]) if isinstance(e, dict)]
    except ValueError:
        return []


def all_rows() -> list[dict]:
    rows = []
    for path in sorted(glob.glob(os.path.join(sl.FULL_WORKDIR, "batch_*.json"))):
        rows += json.load(io.open(path, encoding="utf-8"))
    return rows


def ask(rows=None, answers=ANSWERS, workers=4) -> None:
    rows = rows if rows is not None else json.load(io.open(SAMPLE, encoding="utf-8"))
    have = {}
    if os.path.exists(answers):
        have = {e["id"]: e for e in json.load(io.open(answers, encoding="utf-8"))}
    for _ in range(3):
        todo = [r for r in rows if r["id"] not in have]
        if not todo:
            break
        chunks = [todo[i:i + PER_CALL] for i in range(0, len(todo), PER_CALL)]
        with ThreadPoolExecutor(workers) as pool:
            for chunk, answer in zip(chunks, pool.map(_safe, chunks)):
                wanted = {r["id"] for r in chunk}
                for entry in answer:
                    if entry.get("id") in wanted:
                        have[entry["id"]] = entry
                json.dump(list(have.values()), io.open(answers, "w", encoding="utf-8", newline="\n"),
                          ensure_ascii=False)
        json.dump(list(have.values()), io.open(answers, "w", encoding="utf-8", newline="\n"),
                  ensure_ascii=False, indent=1)
    print(len(have), "of", len(rows), "answered")


def _safe(chunk):
    try:
        return _call(chunk)
    except Exception as exc:  # network or API error: the pass loop retries what is missing
        print("call failed:", type(exc).__name__)
        return []


def compare() -> None:
    store = json.load(io.open(sl.FULL_STORE, encoding="utf-8"))["strategies"]
    rows = json.load(io.open(SAMPLE, encoding="utf-8"))
    other = {e["id"]: e for e in json.load(io.open(ANSWERS, encoding="utf-8"))}
    agree, both, n, per = 0, 0, 0, {}
    disagree = []
    for r in rows:
        b = other.get(r["id"])
        if not b:
            continue
        n += 1
        a = store[r["id"]]
        sa = {l["label"] for l in a["labels"] if l["confidence"] != "low"}
        sb = {l.get("label") for l in b.get("labels", []) if l.get("confidence") != "low"}
        hit = a["primary"] == b.get("primary")
        agree += hit
        both += bool(sa & sb) or (not sa and not sb)
        s = per.setdefault(r["stratum"], [0, 0])
        s[0] += hit
        s[1] += 1
        if not hit:
            disagree.append({"id": r["id"], "haiku": a["primary"], "deepseek": b.get("primary"),
                             "haiku_labels": sorted(sa), "deepseek_labels": sorted(sb)})
    print("compared %d: primary equal %d (%.0f%%), at least one shared label %d (%.0f%%)" % (
        n, agree, 100 * agree / n, both, 100 * both / n))
    total = sum(json.load(io.open(SAMPLE, encoding="utf-8"))[0].get("stratum_size", 0) for _ in [0])
    for k, (h, t) in sorted(per.items()):
        print("  %-16s %2d/%-2d" % (k, h, t))
    json.dump(disagree, io.open(os.path.join(DIR, "disagreements.json"), "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, indent=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--draw", action="store_true")
    parser.add_argument("--ask", action="store_true")
    parser.add_argument("--compare", action="store_true")
    parser.add_argument("--all", action="store_true", help="second opinion on every strategy -> deepseek_all.json")
    args = parser.parse_args()
    if args.all:
        ask(all_rows(), os.path.join(DIR, "deepseek_all.json"), workers=8)
    if args.draw:
        draw()
    if args.ask:
        ask()
    if args.compare:
        compare()
