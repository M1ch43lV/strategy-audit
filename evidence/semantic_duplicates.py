# -*- coding: utf-8 -*-
"""Find renamed strategy implementations with identical executable code.

This is deliberately separate from :mod:`evidence.new_repo_candidates`.
That module asks whether a newly discovered *name* is already represented;
this one audits the already canonicalized local corpus without network access.
It emits evidence only.  It never changes an adjudication, status CSV, or
benchmark input: a human still selects the representative for a confirmed
group before a later decision writer can exclude the redundant members.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
import os
import sys
import tokenize
from collections import defaultdict


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES = os.path.join(ROOT, "evidence", "EXECUTION_PROFILES.csv")
FULL_MANIFEST = os.path.join(ROOT, "results", "regime", "full_backtest_manifest.json")
OUTPUT_JSON = os.path.join(ROOT, "evidence", "SEMANTIC_DUPLICATES.json")
OUTPUT_MD = os.path.join(ROOT, "evidence", "SEMANTIC_DUPLICATES.md")
ADJUDICATION = os.path.join(ROOT, "evidence", "SEMANTIC_DUPLICATE_ADJUDICATION.json")


def _read_csv(path):
    with io.open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def normalized_ast_digest(source, strategy_id):
    """Hash executable tokens while safely neutralising its class label.

    Comments and non-significant whitespace are omitted from the token stream.
    A one-line ``typing`` import is removed only if none of its imported names
    appears elsewhere in the source;
    that handles the known harmless ``..._75fix`` import without erasing type
    annotations or a runtime name lookup.  References to the class elsewhere
    remain intact, so a strategy that uses its own class identity is not
    incorrectly equated with a renamed copy.
    """
    lines = source.splitlines(keepends=True)
    token_rows = list(tokenize.generate_tokens(io.StringIO(source).readline))
    import_names = set()
    for index, token in enumerate(token_rows[:-2]):
        if token.type == tokenize.NAME and token.string == "from" and \
                token_rows[index + 1].string == "typing" and token_rows[index + 2].string == "import":
            line = lines[token.start[0] - 1]
            import_names.update(name.strip().split(" as ")[0] for name in line.split("import", 1)[1].split(","))
    used_names = {token.string for token in token_rows if token.type == tokenize.NAME}
    removable_lines = set()
    if import_names and all(source.count(name) == 1 for name in import_names):
        removable_lines = {token.start[0] for index, token in enumerate(token_rows[:-2])
                           if token.type == tokenize.NAME and token.string == "from"
                           and token_rows[index + 1].string == "typing"
                           and token_rows[index + 2].string == "import"}
    tokens = []
    previous = ""
    class_pending = False
    for token in token_rows:
        if token.start[0] in removable_lines or token.type in (tokenize.COMMENT, tokenize.NL):
            continue
        value = token.string
        if token.type == tokenize.STRING:
            try:
                value = repr(ast.literal_eval(token.string))
            except (SyntaxError, ValueError):
                pass
        if token.type == tokenize.NAME and token.string == "class":
            class_pending = True
        elif class_pending and token.type == tokenize.NAME:
            if token.string == strategy_id:
                value = "__CANONICAL_STRATEGY_CLASS__"
            class_pending = False
        elif token.type not in (tokenize.INDENT, tokenize.DEDENT, tokenize.NEWLINE):
            class_pending = False
        tokens.append((token.type, value))
        previous = value
    return "sha256_" + hashlib.sha256(
        repr(tokens).encode("utf-8")
    ).hexdigest()


def _full_results(path=FULL_MANIFEST):
    if not os.path.exists(path):
        return {}
    with io.open(path, encoding="utf-8") as handle:
        return (json.load(handle).get("results") or {})


def build(profile_path=PROFILES, full_manifest_path=FULL_MANIFEST):
    """Return only code-equivalent groups, enriched with measured evidence."""
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 20000))
    groups = defaultdict(list)
    unreadable = []
    for profile in _read_csv(profile_path):
        path = os.path.join(ROOT, profile["canonical_file"].replace("/", os.sep))
        try:
            with io.open(path, encoding="utf-8") as handle:
                digest = normalized_ast_digest(handle.read(), profile["strategy_id"])
        except (OSError, SyntaxError, RecursionError) as exc:
            unreadable.append({"strategy_id": profile["strategy_id"], "error": type(exc).__name__})
            continue
        groups[digest].append(profile)

    full = _full_results(full_manifest_path)
    result = []
    for digest, members in sorted(groups.items()):
        if len(members) < 2:
            continue
        entries = []
        measured_hashes = set()
        for profile in sorted(members, key=lambda row: row["strategy_id"].lower()):
            measurement = full.get(profile["strategy_id"], {})
            trade_hash = measurement.get("trades_sha256", "") if measurement.get("status") == "measured" else ""
            if trade_hash:
                measured_hashes.add(trade_hash)
            entries.append({
                "strategy_id": profile["strategy_id"],
                "canonical_file": profile["canonical_file"],
                "repo": profile["repo"],
                "run_profile": profile["run_profile"],
                "full_backtest_status": measurement.get("status", "not_run"),
                "trades": measurement.get("trades", ""),
                "trades_sha256": trade_hash,
            })
        measured_n = sum(bool(entry["trades_sha256"]) for entry in entries)
        result.append({
            "normalized_ast_sha256": digest,
            "members": entries,
            "measured_members": measured_n,
            "trade_hashes": sorted(measured_hashes),
            "evidence_status": "confirmed_same_trades" if measured_n >= 2 and len(measured_hashes) == 1 else "code_equivalent_only",
        })
    return {"schema_version": 1, "groups": result, "unreadable": unreadable}


def _json_bytes(data):
    return (json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def adjudicate(data):
    """Apply the owner-approved, evidence-bound duplicate rule.

    One measured member is retained. Shorter unsuffixed names win ties so
    obvious labels such as ``foo`` are preferred over ``foofix``; the final
    lexical key makes regeneration deterministic. Code-only groups never
    produce exclusions.
    """
    decisions = []
    for group in data["groups"]:
        if group["evidence_status"] != "confirmed_same_trades":
            continue
        measured = [member for member in group["members"] if member["trades_sha256"]]
        representative = min(
            measured, key=lambda member: (len(member["strategy_id"]),
                                           member["strategy_id"].casefold(),
                                           member["strategy_id"]))
        for member in group["members"]:
            if member["strategy_id"] == representative["strategy_id"]:
                continue
            decisions.append({
                "strategy_id": member["strategy_id"],
                "decision": "excluded_duplicate_implementation",
                "canonical_representative": representative["strategy_id"],
                "normalized_ast_sha256": group["normalized_ast_sha256"],
                "trades_sha256": representative["trades_sha256"],
                "evidence_rule": "normalized_code_and_identical_full_backtest_trades_v1",
            })
    return {"schema_version": 1, "decisions": sorted(decisions, key=lambda row: row["strategy_id"].casefold())}


def _report(data):
    lines = [
        "# Semantic duplicate candidates", "",
        "Generated by `evidence.semantic_duplicates`.  Equal normalized ASTs are",
        "candidate evidence, not an automatic exclusion.  `confirmed_same_trades`",
        "additionally means two or more canonical full backtests share one trade hash.", "",
    ]
    for group in data["groups"]:
        lines += ["## `%s` - %s" % (group["normalized_ast_sha256"], group["evidence_status"]), "",
                  "| Strategy | Full backtest | Trades | Trade hash |", "|---|---|---:|---|"]
        for member in group["members"]:
            lines.append("| `%s` | `%s` | %s | `%s` |" % (
                member["strategy_id"], member["full_backtest_status"],
                member["trades"] or "-", member["trades_sha256"] or "-"))
        lines.append("")
    return ("\n".join(lines) + "\n").encode("utf-8")


def _write(path, content):
    temporary = path + ".tmp"
    with io.open(temporary, "wb") as handle:
        handle.write(content)
    os.replace(temporary, path)


def selftest():
    plain = "class Alpha:\n    value = 1\n"
    renamed = "from typing import Dict, List\nclass Beta:\n    value = 1\n"
    assert normalized_ast_digest(plain, "Alpha") == normalized_ast_digest(renamed, "Beta")
    used_typing = "from typing import Dict\nclass Beta:\n    value: Dict[str, int] = {}\n"
    assert normalized_ast_digest(plain, "Alpha") != normalized_ast_digest(used_typing, "Beta")
    print("semantic_duplicates selftest: PASS")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--check", action="store_true", help="fail when generated evidence is stale")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    data = build()
    decisions = adjudicate(data)
    outputs = ((OUTPUT_JSON, _json_bytes(data)), (OUTPUT_MD, _report(data)),
               (ADJUDICATION, _json_bytes(decisions)))
    if args.check:
        stale = [path for path, content in outputs if not os.path.exists(path) or open(path, "rb").read() != content]
        if stale:
            print("semantic duplicate evidence stale: %s" % ", ".join(stale))
            return 1
        print("semantic duplicate evidence current")
        return 0
    for path, content in outputs:
        _write(path, content)
    print("semantic duplicates: %d groups, %d exclusions, %d unreadable" % (
        len(data["groups"]), len(decisions["decisions"]), len(data["unreadable"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
