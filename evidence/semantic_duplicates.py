# -*- coding: utf-8 -*-
"""Find renamed strategy implementations with identical executable code.

This is deliberately separate from :mod:`evidence.new_repo_candidates`.
That module asks whether a newly discovered *name* is already represented;
this one audits the already canonicalized local corpus without network access.
`adjudicate()` writes final exclusion decisions automatically (owner-approved
rule, no per-group human step) to `SEMANTIC_DUPLICATE_ADJUDICATION.json`,
which `evidence.strategy_status` reads directly - this module does not itself
touch the status CSV, a benchmark input, or any file on disk beyond its own
three JSON/MD outputs. It never deletes a source file; `tools.harvest`'s own
`remove_semantic_duplicates()` is the only place that acts on
`duplicate_source_files()`'s resolved paths.
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


def _json_bytes(data):
    return (json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def adjudicate(data, class1=None):
    """Apply the owner-approved duplicate rule - two evidence tiers, both
    final exclusions.

    2026-09-16: normalized code identity alone is now sufficient, an
    owner decision made after this tool's previous, more cautious design
    (`pre_stage1_hold` - now retired) held 102 269-batch rows in permanent
    limbo. That design only ever promoted a hold into an exclusion once a
    SECOND, independently full-backtested member confirmed an identical
    trade hash - but a held row is by construction withheld from Stage 1,
    so it can never reach the full backtest that confirmation requires.
    102 rows sat waiting for evidence the hold itself made unreachable.

    Tier 1, strongest, unchanged: `evidence_status == "confirmed_same_trades"`
    - two or more members independently full-backtested with one shared
    trade hash.

    Tier 2, new: normalized AST identical, AND no config overlay detectable
    on either side (`PROFILE_CLASS1.json` or a companion params file - see
    `_has_own_config_overlay`), AND no existing measurement contradicts
    equivalence. That last clause is load-bearing, not theoretical:
    `MACDStrategyADA`/`AVAX`/`BTC`/`ENJ`/`ETC`/`SOL`/`XRP` are byte-identical
    after class-name normalization yet measured seven DIFFERENT trade
    counts - `_has_own_config_overlay` catches ADA/BTC specifically (a
    same-named `.json` params file), but a group with two or more measured,
    disagreeing trade hashes is direct proof of non-equivalence regardless
    of whether the mechanism is known, and is never excluded here even if
    every other tier-2 condition holds.

    One measured member is retained when any exist (tier 1) or the same
    shorter-unsuffixed-name tie-break `_pick_representative` uses otherwise
    (tier 2, which may have no measurement to prefer at all). The final
    lexical key makes regeneration deterministic.
    """
    class1 = _load_profile_class1() if class1 is None else class1
    decisions = []
    for group in data["groups"]:
        if group["evidence_status"] == "confirmed_same_trades":
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
            continue
        if len(group["trade_hashes"]) > 1:
            continue  # measured disagreement - direct proof, never excluded
        representative = _pick_representative(group["members"])
        rep_overlay = _has_own_config_overlay(
            representative["strategy_id"], representative["canonical_file"], class1)
        for member in group["members"]:
            if member["strategy_id"] == representative["strategy_id"]:
                continue
            if rep_overlay or _has_own_config_overlay(
                    member["strategy_id"], member["canonical_file"], class1):
                continue
            decisions.append({
                "strategy_id": member["strategy_id"],
                "decision": "excluded_duplicate_implementation",
                "canonical_representative": representative["strategy_id"],
                "normalized_ast_sha256": group["normalized_ast_sha256"],
                "trades_sha256": "",
                "evidence_rule": "normalized_code_match_no_config_overlay_either_side_v1",
            })
    return {"schema_version": 1, "decisions": sorted(decisions, key=lambda row: row["strategy_id"].casefold())}


def duplicate_source_files(decisions, profiles=None):
    """Resolve each excluded row to the source file harvest.py wrote,
    ready for a caller to delete - this module only computes, never
    deletes (`tools.harvest.remove_semantic_duplicates` and the retroactive
    cleanup script are the only callers that actually touch disk).
    `original_file`, not `canonical_file`: the latter can point at a
    `repair/patched/` overlay, which is not what harvest.py downloaded and
    not what should be removed. A strategy_id EXECUTION_PROFILES.csv no
    longer lists (already removed, or never harvested at all) is skipped
    rather than raising - the caller may be re-running over a partially
    cleaned corpus.

    Two safety exclusions, found necessary 2026-09-16 (REGISTER.md Phase 17
    addendum) after an 11-strategy loss this way: `adjudicate()` decides
    each duplicate GROUP independently, so a strategy can be the KEPT
    representative of one group while simultaneously being the EXCLUDED
    member of a different group (`BinClucMadv1` was representative for
    `BinClucMadSMAv1`/`SMAv2`/`v2` while itself excluded as a duplicate of
    something else) - deleting it then orphans its own group's members,
    which still point at a representative that no longer exists. Never
    delete a strategy_id cited as ANY entry's `canonical_representative`
    here, regardless of its own exclusion status; the adjudication record
    still marks it excluded (correct for STRATEGY_STATUS.csv's cohort),
    only the physical file is spared. Symmetrically, never delete a file
    that a currently-kept (non-excluded) strategy_id also resolves to -
    two classes sharing one physical file is not this corpus's common
    case, but silently deleting a live class alongside an excluded one in
    the same file would be the same shape of loss by a different route.
    """
    if profiles is None:
        profiles = {row["strategy_id"]: row for row in _read_csv(PROFILES)}
    excluded_ids = {entry["strategy_id"] for entry in decisions["decisions"]}
    protected_reps = {entry["canonical_representative"]
                      for entry in decisions["decisions"]
                      if entry.get("canonical_representative")}
    live_files = {row["original_file"] for sid, row in profiles.items()
                 if sid not in excluded_ids}
    resolved = []
    for entry in decisions["decisions"]:
        strategy_id = entry["strategy_id"]
        if strategy_id in protected_reps:
            continue
        row = profiles.get(strategy_id)
        if row is None:
            continue
        if row["original_file"] in live_files:
            continue
        resolved.append({"strategy_id": strategy_id,
                         "canonical_representative": entry["canonical_representative"],
                         "evidence_rule": entry["evidence_rule"],
                         "original_file": row["original_file"]})
    return resolved


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


def _member(strategy_id, trades="", trades_sha256=""):
    return {"strategy_id": strategy_id, "canonical_file": "repos/x/%s.py" % strategy_id,
            "repo": "x/y", "run_profile": "spot_long", "full_backtest_status":
            "measured" if trades_sha256 else "not_run", "trades": trades,
            "trades_sha256": trades_sha256}


def selftest():
    plain = "class Alpha:\n    value = 1\n"
    renamed = "from typing import Dict, List\nclass Beta:\n    value = 1\n"
    assert normalized_ast_digest(plain, "Alpha") == normalized_ast_digest(renamed, "Beta")
    used_typing = "from typing import Dict\nclass Beta:\n    value: Dict[str, int] = {}\n"
    assert normalized_ast_digest(plain, "Alpha") != normalized_ast_digest(used_typing, "Beta")

    # Tier 1, unchanged: two independently full-backtested members share one
    # trade hash - the third, unmeasured member rides along on that proof.
    tier1 = {"groups": [{
        "normalized_ast_sha256": "sha_a", "evidence_status": "confirmed_same_trades",
        "trade_hashes": ["sha_trades"],
        "members": [_member("Foo", 10, "sha_trades"), _member("FooTwin", 10, "sha_trades"),
                    _member("FooThird")],
    }]}
    decisions = adjudicate(tier1, class1={})
    excluded = {d["strategy_id"] for d in decisions["decisions"]}
    assert excluded == {"FooThird", "FooTwin"}, excluded  # "Foo" is the shorter, retained name
    assert all(d["evidence_rule"] == "normalized_code_and_identical_full_backtest_trades_v1"
              for d in decisions["decisions"])

    # Tier 2, new: code-identical, nothing measured yet, no config overlay -
    # excluded on code identity alone. This is the exact shape that used to
    # sit forever in pre_stage1_hold, unable to ever reach tier 1's bar.
    tier2 = {"groups": [{
        "normalized_ast_sha256": "sha_b", "evidence_status": "code_equivalent_only",
        "trade_hashes": [],
        "members": [_member("Bar"), _member("BarTwin")],
    }]}
    decisions = adjudicate(tier2, class1={})
    assert {d["strategy_id"] for d in decisions["decisions"]} == {"BarTwin"}
    assert decisions["decisions"][0]["evidence_rule"] == \
        "normalized_code_match_no_config_overlay_either_side_v1"

    # A config overlay on either side blocks tier 2 for that member - code
    # identity alone does not prove behavioural identity here (the
    # MACDStrategyADA/BTC shape: a companion params file changes the run).
    decisions = adjudicate(tier2, class1={"BarTwin": {"rules": ["x"]}})
    assert decisions["decisions"] == []

    # Measured disagreement is direct proof of non-equivalence and blocks
    # tier 2 outright, even though nothing else here would have. This is
    # the actual MACDStrategy* shape: same code, seven different measured
    # trade counts, still not excluded.
    macd_like = {"groups": [{
        "normalized_ast_sha256": "sha_c", "evidence_status": "code_equivalent_only",
        "trade_hashes": ["sha_x", "sha_y"],
        "members": [_member("MacdA", 10, "sha_x"), _member("MacdB", 20, "sha_y")],
    }]}
    assert adjudicate(macd_like, class1={})["decisions"] == []

    # duplicate_source_files()'s two safety guards, found necessary after an
    # 11-strategy loss this way (REGISTER.md Phase 17 addendum).
    decisions = {"decisions": [
        # Ordinary case: excluded, own unique file, no conflict - resolves.
        {"strategy_id": "Dup1", "canonical_representative": "Keep1",
         "evidence_rule": "r"},
        # BinClucMadv1 shape: Dup2 is EXCLUDED here (as someone else's
        # duplicate) while ALSO being cited as the representative other
        # entries depend on - must not be deleted despite its own exclusion.
        {"strategy_id": "Dup2", "canonical_representative": "SomeoneElse",
         "evidence_rule": "r"},
        {"strategy_id": "Dup2Child", "canonical_representative": "Dup2",
         "evidence_rule": "r"},
        # Dup3 shares its physical file with Keep3, which is NOT excluded -
        # deleting the file would take Keep3 down with it.
        {"strategy_id": "Dup3", "canonical_representative": "Keep3",
         "evidence_rule": "r"},
    ]}
    profiles = {
        "Dup1": {"original_file": "repos/x/dup1.py"},
        "Dup2": {"original_file": "repos/x/dup2.py"},
        "Dup2Child": {"original_file": "repos/x/dup2child.py"},
        "Dup3": {"original_file": "repos/x/shared.py"},
        "Keep3": {"original_file": "repos/x/shared.py"},
    }
    resolved = {r["strategy_id"] for r in duplicate_source_files(decisions, profiles)}
    assert resolved == {"Dup1", "Dup2Child"}, resolved

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
