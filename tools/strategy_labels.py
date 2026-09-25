# -*- coding: utf-8 -*-
"""strategy_labels - logic labels for strategies, read by a small model, checked by rules.

PILOT. The store written here, ``evidence/STRATEGY_LABELS_PILOT.json``, is a
separate store on purpose; it merges into the shared strategy table only after the
pilot's agreement numbers are accepted. Nothing here is a measurement and no
stage reads it.

TWO LAYERS, KEPT APART.
* Facts (mechanical, no model): timeframe, speed class, can_short, leverage
  hook, position adjustment (DCA), ML imports, custom stoploss/exit hooks.
  ``scalper`` is a speed fact (timeframe <= 5m), as in
  ``tools/strategy_classification.py``, never a model's opinion.
* Logic labels (interpretation, multi-label): the vocabulary and definitions
  are in ``tools/strategy_labels_prompt.txt``. The model reads a fact sheet of
  the strategy's own code and must copy a verbatim evidence snippet per label;
  ``ingest`` demotes any label whose snippet is not in the sheet.

The prompt's sha256 and the model name are stored with every batch, so a label
can be tied to what produced it. Family labels come from the family file
``evidence/STRATEGY_FAMILIES.json`` (``tools/strategy_families.py``): a label
belongs to a family when MORE than half of its members carry it; other labels
are kept as ``variant_labels`` with their counts.

Usage:
    python -m tools.strategy_labels --sample 60 --batch-size 15   # pilot batches
    python -m tools.strategy_labels --ingest labels_pilot --model haiku-4.5
    python -m tools.strategy_labels --report
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import os
import random
import re
import sys
from datetime import datetime, timezone

_ROOT = (os.environ.get("AUDIT_ROOT") or
         os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from tools import strategy_families as sf  # noqa: E402
from tools import strategy_ideas as si  # noqa: E402

PROMPT = os.path.join(_ROOT, "tools", "strategy_labels_prompt.txt")
WORKDIR = os.path.join(_ROOT, "evidence", "labels_pilot")
STORE = os.path.join(_ROOT, "evidence", "STRATEGY_LABELS_PILOT.json")
FULL_WORKDIR = os.path.join(_ROOT, "evidence", "labels_full")
FULL_STORE = os.path.join(_ROOT, "evidence", "STRATEGY_LABELS.json")
LABELS = ("trend_following", "momentum", "mean_reversion", "breakout", "volatility",
          "grid", "volume_flow", "pattern", "statistical", "other")
CONFIDENCE = ("high", "medium", "low")
ATTRS = ("timeframe", "minimal_roi", "stoploss", "trailing_stop", "can_short",
         "position_adjustment_enable", "max_entry_position_adjustment", "use_exit_signal",
         "use_sell_signal", "startup_candle_count", "process_only_new_candles")
HOOKS = ("adjust_trade_position", "custom_stoploss", "custom_exit", "custom_sell", "leverage",
         "custom_entry_price", "confirm_trade_entry", "informative_pairs")
ENTRY_NAMES = ("populate_entry_trend", "populate_buy_trend")
EXIT_NAMES = ("populate_exit_trend", "populate_sell_trend")
LIMITS = {"indicators": 1800, "entry": 1600, "exit": 900}
SCALP = {"1m", "3m", "5m"}
INTRADAY = {"15m", "30m", "1h", "2h"}
SWING = {"4h", "6h", "8h", "12h"}


def sha256_file(path: str) -> str:
    with io.open(path, "rb") as handle:
        return "sha256_" + hashlib.sha256(handle.read()).hexdigest()


def prompt_hash() -> str:
    return sha256_file(PROMPT)[:23]


def _strip(source: str) -> str:
    lines = [ln.rstrip() for ln in source.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    return "\n".join(lines)


def _class_node(tree, name):
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    for node in classes:
        if node.name == name:
            return node
    return classes[0] if classes else None


def facts_of(strategy_id: str, profile: dict) -> dict | None:
    path = os.path.join(_ROOT, profile["canonical_file"].replace("/", os.sep))
    try:
        source = si._read(path)
        tree = si._parse(source)
    except (OSError, SyntaxError):
        return None
    node = _class_node(tree, profile.get("strategy") or strategy_id)
    if node is None:
        return None
    attrs, methods = {}, {}
    for item in node.body:
        if isinstance(item, ast.Assign) and len(item.targets) == 1 and isinstance(item.targets[0], ast.Name):
            if item.targets[0].id in ATTRS:
                attrs[item.targets[0].id] = (ast.get_source_segment(source, item.value) or "")[:120]
        elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name) and item.value is not None:
            if item.target.id in ATTRS:
                attrs[item.target.id] = (ast.get_source_segment(source, item.value) or "")[:120]
        elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            methods[item.name] = ast.get_source_segment(source, item) or ""

    def method(names, limit):
        for name in names:
            if name in methods:
                return _strip(methods[name])[:limit]
        return ""

    timeframe = attrs.get("timeframe", "").strip("'\" ") or profile.get("execution_timeframe") or ""
    speed = ("scalp" if timeframe in SCALP else "intraday" if timeframe in INTRADAY
             else "swing" if timeframe in SWING else "position" if timeframe else "unknown")
    can_short = attrs.get("can_short", "").strip() == "True"
    dca = attrs.get("position_adjustment_enable", "").strip() == "True" or "adjust_trade_position" in methods
    ml = bool(re.search(r"\b(freqai|sklearn|torch|tensorflow|xgboost|lightgbm|catboost|keras)\b", source, re.I))
    return {
        "facts": {
            "timeframe": timeframe, "speed": speed, "scalper": speed == "scalp",
            "can_short": can_short, "leverage_hook": "leverage" in methods,
            "futures_capable": can_short or "leverage" in methods,
            "dca": dca, "ml_ai": ml,
            "hooks": sorted(h for h in HOOKS if h in methods),
        },
        "sheet": "\n".join([
            "CLASS ATTRIBUTES", *("%s = %s" % (k, v) for k, v in attrs.items()),
            "HOOKS PRESENT: " + ", ".join(sorted(h for h in HOOKS if h in methods)),
            "INDICATOR CODE", method(("populate_indicators",), LIMITS["indicators"]),
            "ENTRY CODE", method(ENTRY_NAMES, LIMITS["entry"]),
            "EXIT CODE", method(EXIT_NAMES, LIMITS["exit"]),
        ]),
        "source_sha256": sha256_file(path),
    }


def pilot_sample(families: list[dict], n: int, seed: int = 20260925) -> list[str]:
    """Stratified pilot: families of every size class, up to three members each,
    spread over the family's sorted members so early and late revisions both appear."""
    rng = random.Random(seed)
    multi = [f for f in families if f["size"] >= 2]
    bins = [(2, 2), (3, 5), (6, 12), (13, 10 ** 6)]
    chosen: list[dict] = []
    per_bin = max(1, n // 3 // len(bins))
    for low, high in bins:
        pool = [f for f in multi if low <= f["size"] <= high]
        rng.shuffle(pool)
        chosen += pool[:per_bin]
    ids: list[str] = []
    for family in chosen:
        members = family["members"]
        take = members if len(members) <= 3 else [members[0], members[len(members) // 2], members[-1]]
        ids += take
    return ids[:n]


def cmd_all(batch_size: int) -> int:
    """Write one sheet batch per `batch_size` strategies for the whole corpus (not_applicable skipped)."""
    profiles = si.load_profiles()
    classification = si.load_classification()
    os.makedirs(FULL_WORKDIR, exist_ok=True)
    rows = []
    for strategy_id in sorted(profiles):
        if (classification.get(strategy_id) or {}).get("strategy_type") == "not_applicable":
            continue
        info = facts_of(strategy_id, profiles[strategy_id])
        if info:
            rows.append({"id": strategy_id, "sheet": info["sheet"]})
    for index in range(0, len(rows), batch_size):
        path = os.path.join(FULL_WORKDIR, "batch_%03d.json" % (index // batch_size + 1))
        with io.open(path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(rows[index:index + batch_size], handle, ensure_ascii=False, indent=1)
    print("%d strategies in %d batches -> %s" % (len(rows), -(-len(rows) // batch_size),
                                                 os.path.relpath(FULL_WORKDIR, _ROOT)))
    return 0


def cmd_sample(count: int, batch_size: int) -> int:
    families = sf.build()
    with io.open(sf.OUTPUT, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(families, handle, ensure_ascii=False, indent=1)
    profiles = si.load_profiles()
    ids = pilot_sample(families["families"], count)
    os.makedirs(WORKDIR, exist_ok=True)
    rows = []
    for strategy_id in ids:
        info = facts_of(strategy_id, profiles[strategy_id])
        if info:
            rows.append({"id": strategy_id, "sheet": info["sheet"]})
    for index in range(0, len(rows), batch_size):
        path = os.path.join(WORKDIR, "batch_%02d.json" % (index // batch_size + 1))
        with io.open(path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(rows[index:index + batch_size], handle, ensure_ascii=False, indent=1)
    print("%d strategies from %d families in %d batches -> %s"
          % (len(rows), len({si.family_stem(i) for i in ids}), -(-len(rows) // batch_size),
             os.path.relpath(WORKDIR, _ROOT)))
    return 0


def _norm(text: str) -> str:
    return re.sub(r"\s+", "", text)


def store_item(entry: dict, sheet_norm: str, info: dict) -> dict:
    """One store record from a model answer: evidence not found verbatim in the sheet is demoted to low."""
    labels = []
    for item in entry.get("labels") or []:
        label, conf = item.get("label"), item.get("confidence")
        evidence = str(item.get("evidence") or "")
        flags = []
        if label not in LABELS:
            flags.append("unknown_label")
        if conf not in CONFIDENCE:
            conf = "low"
            flags.append("bad_confidence")
        if not evidence or _norm(evidence) not in sheet_norm:
            conf = "low"
            flags.append("evidence_not_verbatim")
        labels.append({"label": label, "confidence": conf, "evidence": evidence[:160], "flags": flags})
    return {"source_sha256": info["source_sha256"], "facts": info["facts"],
            "primary": entry.get("primary"), "labels": labels, "note": str(entry.get("note") or "")[:120]}


def cmd_ingest(model: str, workdir: str = WORKDIR, store_path: str = STORE) -> int:
    profiles = si.load_profiles()
    old = {}
    if os.path.exists(store_path):
        old = json.load(io.open(store_path, encoding="utf-8")).get("strategies", {})
    store = {"schema": "strategy-labels-1", "prompt_sha256": prompt_hash(), "model": model,
             "labelled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "labels": list(LABELS), "strategies": {}}
    problems = 0
    for name in sorted(os.listdir(workdir)):
        if not name.startswith("result_"):
            continue
        batch = json.load(io.open(os.path.join(workdir, name.replace("result_", "batch_")), encoding="utf-8"))
        sheets = {row["id"]: _norm(row["sheet"]) for row in batch}
        results = json.load(io.open(os.path.join(workdir, name), encoding="utf-8"))
        for entry in results:
            sid = entry.get("id")
            if sid not in sheets:
                problems += 1
                continue
            item = store_item(entry, sheets[sid], facts_of(sid, profiles[sid]))
            previous = old.get(sid) or {}
            if previous.get("second_opinion") and previous.get("primary") == item["primary"]:
                item["second_opinion"] = previous["second_opinion"]
            store["strategies"][sid] = item
            problems += sum(1 for lab in item["labels"] if lab["flags"])
    with io.open(store_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(store, handle, ensure_ascii=False, indent=1)
    print("%d strategies stored, %d label problems -> %s"
          % (len(store["strategies"]), problems, os.path.relpath(store_path, _ROOT)))
    return 0


from tools import label_consensus  # noqa: E402


def family_labels(store: dict, families: dict) -> list[dict]:
    result = []
    for family in families["families"]:
        members = [m for m in family["members"] if m in store["strategies"]]
        if len(family["members"]) < 2 or not members:
            continue
        counts: dict[str, int] = {}
        for member in members:
            for lab in label_consensus.confirmed_labels(store["strategies"][member]):
                counts[lab] = counts.get(lab, 0) + 1
        majority = sorted(k for k, v in counts.items() if v * 2 > len(members))
        result.append({"family": family["family"], "labelled": len(members), "size": family["size"],
                       "labels": majority,
                       "variant_labels": {k: v for k, v in sorted(counts.items()) if k not in majority}})
    return result


def cmd_report(store_path: str = STORE) -> int:
    store = json.load(io.open(store_path, encoding="utf-8"))
    rows = store["strategies"]
    total = sum(len(r["labels"]) for r in rows.values())
    by_conf = {c: sum(1 for r in rows.values() for l in r["labels"] if l["confidence"] == c) for c in CONFIDENCE}
    flagged = sum(1 for r in rows.values() for l in r["labels"] if l["flags"])
    counts = {}
    for r in rows.values():
        for l in r["labels"]:
            counts[l["label"]] = counts.get(l["label"], 0) + 1
    print("%d strategies, %d labels (%.1f per strategy); confidence %s; %d flagged"
          % (len(rows), total, total / max(1, len(rows)), by_conf, flagged))
    print("label counts:", dict(sorted(counts.items(), key=lambda kv: -kv[1])))
    print("no label / other only: %d" % sum(1 for r in rows.values()
          if not r["labels"] or {l["label"] for l in r["labels"]} <= {"other"}))
    print("scalper facts: %d, futures_capable: %d, dca: %d, ml_ai: %d" % tuple(
        sum(1 for r in rows.values() if r["facts"][k]) for k in ("scalper", "futures_capable", "dca", "ml_ai")))
    families = json.load(io.open(sf.OUTPUT, encoding="utf-8"))
    print("family labels (majority > 50%):")
    for fam in family_labels(store, families):
        print("  %-30s %2d/%-3d %-40s variants=%s" % (fam["family"], fam["labelled"], fam["size"],
                                                     ",".join(fam["labels"]) or "-", fam["variant_labels"] or "-"))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--sample", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=15)
    parser.add_argument("--ingest", default="", help="ingest result_*.json from evidence/labels_pilot")
    parser.add_argument("--model", default="")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--all", action="store_true", help="write batches for the whole corpus; with --ingest/--report use the full store")
    args = parser.parse_args(argv)
    if args.all and not (args.ingest or args.report):
        return cmd_all(args.batch_size)
    if args.sample:
        return cmd_sample(args.sample, args.batch_size)
    if args.ingest:
        return (cmd_ingest(args.model or "unknown", FULL_WORKDIR, FULL_STORE) if args.all
                else cmd_ingest(args.model or "unknown"))
    if args.report:
        return cmd_report(FULL_STORE) if args.all else cmd_report()
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
