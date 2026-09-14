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

from evidence import execution_profiles


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES = os.path.join(ROOT, "evidence", "EXECUTION_PROFILES.csv")
FULL_MANIFEST = os.path.join(ROOT, "results", "regime", "full_backtest_manifest.json")
OUTPUT_JSON = os.path.join(ROOT, "evidence", "SEMANTIC_DUPLICATES.json")
OUTPUT_MD = os.path.join(ROOT, "evidence", "SEMANTIC_DUPLICATES.md")
ADJUDICATION = os.path.join(ROOT, "evidence", "SEMANTIC_DUPLICATE_ADJUDICATION.json")
HOLD = os.path.join(ROOT, "evidence", "SEMANTIC_DUPLICATE_HOLD.json")
PROFILE_CLASS1 = os.path.join(ROOT, "evidence", "PROFILE_CLASS1.json")


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


def _pure_inheritance_bases():
    """child -> immediate base, for `EXTRA_SUBCLASS_STRATEGIES` rows whose own
    class body writes no entry/exit column at all - the same condition
    `execution_profiles._inherit_subclass_profiles()` uses to decide whether
    a child's behavioral profile is copied from its base (NFIX7Risk and most
    thin wrappers), never a child that defines its own populate_entry_trend
    (BBRSITV1..5). Re-derived from the child's own source here rather than
    read off `EXECUTION_PROFILES.csv`'s `signal_capability` column: by the
    time that CSV is written, inheritance has already overwritten a matching
    child's `signal_capability` with its base's value, so the column alone
    can no longer tell a true pure-inheritance child apart from one whose own
    (independently computed) profile just happens to match its base's.
    """
    bases = {}
    for rel_path, strategy in execution_profiles.EXTRA_SUBCLASS_STRATEGIES:
        base = execution_profiles.INHERIT_PROFILE_FROM.get(strategy)
        if not base:
            continue
        path = os.path.join(ROOT, "repos", *rel_path.split("/"))
        if not os.path.isfile(path):
            continue
        try:
            node = execution_profiles.strategy_node(path, strategy)
        except (ValueError, SyntaxError, RecursionError):
            continue
        long_entry, short_entry, _methods, _writes = execution_profiles.entry_writes(node)
        if not long_entry and not short_entry:
            bases[strategy] = base
    return bases


def _resolve_digest_key(strategy_id, inherited_from, own_digest):
    """A pure-inheritance child's own file never textually repeats the
    entry/exit logic it inherits, so its own normalized digest cannot match
    a sibling wrapper of the same base - the two would silently sit in
    separate one-member groups forever. Walk up to the nearest ancestor that
    is not itself a pure-inheritance child (a chain resolves in one pass,
    matching `_inherit_subclass_profiles()`'s own chain handling) and group
    under THAT ancestor's own digest instead - the code that actually runs
    for this child. Falls back to the child's own digest if the ancestor is
    unreadable or missing."""
    seen = set()
    current = strategy_id
    while current in inherited_from and current not in seen:
        seen.add(current)
        current = inherited_from[current]
    return own_digest.get(current) or own_digest.get(strategy_id)


def build(profile_path=PROFILES, full_manifest_path=FULL_MANIFEST):
    """Return only code-equivalent groups, enriched with measured evidence."""
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 20000))
    profiles = _read_csv(profile_path)
    inherited_from = _pure_inheritance_bases()

    own_digest = {}
    unreadable = []
    for profile in profiles:
        path = os.path.join(ROOT, profile["canonical_file"].replace("/", os.sep))
        try:
            with io.open(path, encoding="utf-8") as handle:
                own_digest[profile["strategy_id"]] = normalized_ast_digest(
                    handle.read(), profile["strategy_id"])
        except (OSError, SyntaxError, RecursionError) as exc:
            unreadable.append({"strategy_id": profile["strategy_id"], "error": type(exc).__name__})

    groups = defaultdict(list)
    for profile in profiles:
        strategy_id = profile["strategy_id"]
        if strategy_id not in own_digest:
            continue
        key = _resolve_digest_key(strategy_id, inherited_from, own_digest)
        groups[key].append(profile)

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


def _load_profile_class1(path=PROFILE_CLASS1):
    if not os.path.exists(path):
        return {}
    try:
        with io.open(path, encoding="utf-8") as handle:
            return json.load(handle).get("strategies") or {}
    except (ValueError, OSError):
        return {}


def _has_own_config_overlay(strategy_id, canonical_file, class1):
    """True if anything outside this strategy's own normalized source could
    make it behave differently from a code-identical sibling, despite an
    identical `normalized_ast_digest()`.

    Two distinct mechanisms, both silent to a pure source-text comparison:

    - `PROFILE_CLASS1.json` - this audit's own environment-repair overlay
      (`config_source`/`config_keys`/`rules`). The literal check the owner
      asked for.
    - a companion `<file>.json` next to the strategy's own `.py` - freqtrade's
      own auto-load convention (`HyperStrategyMixin.load_params_from_file()`:
      `Path(self.__file__).with_suffix(".json")`), invisible to any source
      read. This is not hypothetical: `MACDStrategyADA`/`MACDStrategyBTC` are
      byte-identical after class-name normalization (`MACDStrategy - ADA.py`
      vs `MACDStrategy - BTC.py`) yet measured 4031 vs 6162 trades - ADA has
      a same-named `.json` with its own tuned `buy`/`sell`/`roi`/`stoploss`
      values, BTC has none. Skipping ADA before measurement on code identity
      alone would have been wrong.

    Either one present on either side of a pair means "not provably the same
    at runtime from source alone" - defer to the existing measured-trade-hash
    gate in `adjudicate()`, same as any other unconfirmed group.
    """
    if strategy_id in class1:
        return True
    full_path = os.path.join(ROOT, canonical_file.replace("/", os.sep))
    companion = os.path.splitext(full_path)[0] + ".json"
    return os.path.isfile(companion)


def _pick_representative(members):
    """Same tie-break `adjudicate()` uses: shorter unsuffixed name wins,
    casefold then exact string breaks a remaining tie. Applied to every
    member here (not just measured ones) - a pre-measurement hold list has
    no measured subset to restrict to yet."""
    return min(members, key=lambda member: (
        len(member["strategy_id"]), member["strategy_id"].casefold(), member["strategy_id"]))


def pre_stage1_hold(data, class1=None):
    """Candidates a Stage 1 batch can skip before spending any measurement on
    them - not an exclusion, a deferral. A group only qualifies when it is
    NOT already `confirmed_same_trades` (that case is `adjudicate()`'s job,
    already excluded) and neither the candidate nor its representative carries
    one of the two overlays `_has_own_config_overlay()` checks. Holding one
    is a bet that the representative's own later measurement will confirm the
    pair identical; if it does not (or the representative itself never gets
    measured), the held row must still run its own Stage 1-7 - nothing here
    removes a row from the corpus, it only reorders when its own measurement
    happens. `evidence.strategy_status` does not read this file; only
    `SEMANTIC_DUPLICATE_ADJUDICATION.json`'s measured-and-confirmed rows ever
    exclude anything.
    """
    class1 = _load_profile_class1() if class1 is None else class1
    decisions = []
    for group in data["groups"]:
        if group["evidence_status"] == "confirmed_same_trades":
            continue
        representative = _pick_representative(group["members"])
        rep_overlay = _has_own_config_overlay(
            representative["strategy_id"], representative["canonical_file"], class1)
        for member in group["members"]:
            if member["strategy_id"] == representative["strategy_id"]:
                continue
            if member["full_backtest_status"] == "measured":
                continue  # already has its own measurement; nothing to defer
            if rep_overlay or _has_own_config_overlay(
                    member["strategy_id"], member["canonical_file"], class1):
                continue
            decisions.append({
                "strategy_id": member["strategy_id"],
                "decision": "hold_pending_representative_confirmation",
                "canonical_representative": representative["strategy_id"],
                "normalized_ast_sha256": group["normalized_ast_sha256"],
                "evidence_rule": "normalized_code_match_no_config_overlay_either_side_v1",
            })
    return {"schema_version": 1, "decisions": sorted(decisions, key=lambda row: row["strategy_id"].casefold())}


def filter_targets(strategy_ids, hold_data=None):
    """Split a Stage 1 target list into (proceed, held) using a fresh
    `pre_stage1_hold()` run - the actual "explicit filter before Stage 1
    starts" this is for. `proceed` keeps the input order; `held` carries each
    dropped strategy's representative so the caller can report why."""
    if hold_data is None:
        hold_data = pre_stage1_hold(build())
    held = {row["strategy_id"]: row["canonical_representative"] for row in hold_data["decisions"]}
    wanted = set(strategy_ids)
    proceed = [s for s in strategy_ids if s not in held]
    dropped = [{"strategy_id": s, "canonical_representative": held[s]}
              for s in strategy_ids if s in held and s in wanted]
    return proceed, dropped


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
    parser.add_argument("--filter-file", metavar="PATH",
                        help="Stage 1 target list (one strategy_id per line, "
                             "or 'name<TAB>path' like repair/run_freqai.py's "
                             "input) - print which names can be held back "
                             "pending their representative's own measurement, "
                             "write the rest to PATH.filtered untouched, and "
                             "exit without regenerating any evidence file.")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    data = build()
    decisions = adjudicate(data)
    hold = pre_stage1_hold(data)
    if args.filter_file:
        lines = [line.rstrip("\n") for line in io.open(args.filter_file, encoding="utf-8")
                if line.strip() and not line.startswith("#")]
        names = [line.split("\t")[0] for line in lines]
        proceed, dropped = filter_targets(names, hold)
        by_name = dict(zip(names, lines))
        out_path = args.filter_file + ".filtered"
        with io.open(out_path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(by_name[name] for name in proceed) + ("\n" if proceed else ""))
        print("%d of %d proceed to Stage 1 -> %s" % (len(proceed), len(names), out_path))
        for row in dropped:
            print("  held: %-30s pending %s" % (row["strategy_id"], row["canonical_representative"]))
        return 0
    outputs = ((OUTPUT_JSON, _json_bytes(data)), (OUTPUT_MD, _report(data)),
               (ADJUDICATION, _json_bytes(decisions)), (HOLD, _json_bytes(hold)))
    if args.check:
        stale = [path for path, content in outputs if not os.path.exists(path) or open(path, "rb").read() != content]
        if stale:
            print("semantic duplicate evidence stale: %s" % ", ".join(stale))
            return 1
        print("semantic duplicate evidence current")
        return 0
    for path, content in outputs:
        _write(path, content)
    print("semantic duplicates: %d groups, %d exclusions, %d pre-stage1 holds, %d unreadable" % (
        len(data["groups"]), len(decisions["decisions"]), len(hold["decisions"]), len(data["unreadable"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
