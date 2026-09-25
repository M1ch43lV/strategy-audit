# -*- coding: utf-8 -*-
"""label_intake - label new or changed strategies at harvest time and apply the second-opinion rule.

Step of `tools.harvest.refresh_intake_evidence`. For every strategy without a record in
`evidence/STRATEGY_LABELS.json`, or whose source changed since it was labelled:

1. Haiku 4.5 (`claude -p --model haiku`, `tools.label_runner.ask`) reads the fact sheet.
2. If the answer falls under `tools.label_consensus.needs_second_opinion` (trend_following,
   momentum, breakout, volatility or grid as primary or at high/medium confidence), DeepSeek
   (`tools.label_check`) labels the same sheet blind, and the record keeps that answer as
   `second_opinion`. `tools.label_consensus.status` then says confirmed / contested.

Never fatal: without the `claude` CLI or a DeepSeek key the strategy stays unlabelled or
`pending` and the next intake completes it. `--second-opinion-only` fills the second opinion
for records that need one and lack it.

    python -m tools.label_intake [--limit N] [--dry-run]
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

from tools import label_check, label_consensus, label_runner  # noqa: E402
from tools import strategy_labels as sl  # noqa: E402
from tools import strategy_ideas as si  # noqa: E402

BATCH = 30


def _chunks(rows, size):
    return [rows[i:i + size] for i in range(0, len(rows), size)]


def _load():
    if os.path.exists(sl.FULL_STORE):
        return json.load(io.open(sl.FULL_STORE, encoding="utf-8"))
    return {"schema": "strategy-labels-1", "prompt_sha256": sl.prompt_hash(), "model": "claude-haiku-4-5",
            "labels": list(sl.LABELS), "strategies": {}}


def _save(store):
    with io.open(sl.FULL_STORE, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(store, handle, ensure_ascii=False, indent=1)


def second_opinion(store, sheets) -> int:
    """Ask DeepSeek for every record under the rule that has no second opinion yet."""
    todo = [sid for sid, item in store["strategies"].items()
            if label_consensus.status(item) == "pending" and sid in sheets]
    done = 0
    for chunk in _chunks(todo, label_check.PER_CALL):
        rows = [{"id": sid, "sheet": sheets[sid]} for sid in chunk]
        for entry in label_check._safe(rows):
            sid = entry.get("id")
            if sid not in chunk:
                continue
            checked = sl.store_item(entry, sl._norm(sheets[sid]), store["strategies"][sid])
            store["strategies"][sid]["second_opinion"] = {
                "model": label_check.MODEL, "primary": checked["primary"],
                "labels": [{"label": l["label"], "confidence": l["confidence"]} for l in checked["labels"]]}
            done += 1
    return done


def merge_existing(store, sheets, answers_path=None) -> int:
    """Attach answers of an earlier `label_check --all` run, so they are not paid for twice."""
    answers_path = answers_path or os.path.join(label_check.DIR, "deepseek_all.json")
    if not os.path.exists(answers_path):
        return 0
    have = {e["id"]: e for e in json.load(io.open(answers_path, encoding="utf-8"))}
    done = 0
    for sid, item in store["strategies"].items():
        entry = have.get(sid)
        if not entry or item.get("second_opinion") or sid not in sheets:
            continue
        if not label_consensus.needs_second_opinion(item):
            continue
        checked = sl.store_item(entry, sl._norm(sheets[sid]), item)
        item["second_opinion"] = {
            "model": label_check.MODEL, "primary": checked["primary"],
            "labels": [{"label": l["label"], "confidence": l["confidence"]} for l in checked["labels"]]}
        done += 1
    return done


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--second-opinion-only", action="store_true")
    args = parser.parse_args(argv)
    store = _load()
    profiles = si.load_profiles()
    classification = si.load_classification()
    sheets, facts = {}, {}
    for sid, profile in profiles.items():
        if (classification.get(sid) or {}).get("strategy_type") == "not_applicable":
            continue
        info = sl.facts_of(sid, profile)
        if info:
            sheets[sid], facts[sid] = info["sheet"], info
    pending = [sid for sid in sorted(sheets)
               if (store["strategies"].get(sid) or {}).get("source_sha256") != facts[sid]["source_sha256"]]
    if args.limit:
        pending = pending[:args.limit]
    print("logic labels: %d strategies to label, %d record(s) waiting for a second opinion" % (
        0 if args.second_opinion_only else len(pending),
        sum(1 for i in store["strategies"].values() if label_consensus.status(i) == "pending")), flush=True)
    if args.dry_run:
        return 0
    labelled = 0
    try:
        if not args.second_opinion_only:
            for chunk in _chunks(pending, BATCH):
                rows = [{"id": sid, "sheet": sheets[sid]} for sid in chunk]
                answers = {e["id"]: e for e in label_runner.ask(rows) if e.get("id") in chunk}
                for sid, entry in answers.items():
                    store["strategies"][sid] = sl.store_item(entry, sl._norm(sheets[sid]), facts[sid])
                    labelled += 1
                _save(store)
        merge_existing(store, sheets)
        checked = second_opinion(store, sheets)
        _save(store)
        print("labelled %d, second opinion for %d" % (labelled, checked), flush=True)
    except Exception as exc:  # intake must not fail because a model is unreachable
        _save(store)
        print("logic labels incomplete (%s: %s); the next intake continues" % (type(exc).__name__, exc), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
