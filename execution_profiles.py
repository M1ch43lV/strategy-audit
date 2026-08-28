# -*- coding: utf-8 -*-
"""Build the deduplicated canonical corpus and static execution profiles.

This is an inventory, not a backtest.  It separates what source code can emit
from what a particular run actually emitted.  In particular, ``can_short`` is
not treated as proof of reachable short entries, and absence of short trades in
one window is never treated as proof that no short path exists.

The repository's historical unit is the class name: alphabetical traversal of
``repos/`` selects the first occurrence.  This script deliberately reuses that
rule so its rows join the existing ledger instead of inventing a second corpus.
"""
from __future__ import print_function

import argparse
import ast
import csv
import hashlib
import io
import json
import os
import sys
import warnings


ROOT = os.path.dirname(os.path.abspath(__file__))
REPOS = os.path.join(ROOT, "repos")
DEFAULT_REPAIR = os.path.join(ROOT, "repair")
FIELDS = [
    "strategy_id", "implementation_id", "strategy", "repo", "original_file",
    "canonical_file", "canonical_population", "repair_class", "repair_rules",
    "environment_repair_status", "environment_repair_rules",
    "equivalence_status", "source_tree", "variant", "ledger_present",
    "original_measured_spot", "historical_is_trades", "historical_os_trades",
    "historical_full_measured", "canonical_measured", "declared_timeframe",
    "execution_timeframe", "timeframe_source", "declared_can_short",
    "static_long_entry", "static_short_entry", "signal_capability", "direction_capability",
    "has_leverage_callback", "artifact_role", "author_mode_intent", "mode_support",
    "run_profile", "validated_modes",
    "runtime_smoke_status", "runtime_smoke_timerange", "observed_long_trades",
    "observed_short_trades", "canonical_observed_trades", "trade_evidence_source",
    "runtime_config_sha256", "evidence_level",
    "classification_status", "classification_reason", "source_sha256",
]


def _name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _is_strategy(node):
    return isinstance(node, ast.ClassDef) and any(
        _name(base) == "IStrategy" for base in node.bases
    )


def _read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def discover(repos=REPOS):
    """Return the same first-by-class-name corpus used by corpus.py."""
    seen = set()
    rows = []
    for directory in sorted(os.listdir(repos)):
        repo_root = os.path.join(repos, directory)
        if not os.path.isdir(repo_root):
            continue
        repo = directory.replace("_", "/", 1)
        found = []
        for dirpath, dirs, names in os.walk(repo_root):
            dirs[:] = sorted(d for d in dirs if d not in (
                ".git", "__pycache__", ".venv", "venv", "ftenv",
                "node_modules", ".tox", "site-packages",
            ))
            for filename in sorted(names):
                if not filename.endswith(".py"):
                    continue
                path = os.path.join(dirpath, filename)
                try:
                    source = _read(path)
                    if "IStrategy" not in source:
                        continue
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", SyntaxWarning)
                        tree = ast.parse(source, filename=path)
                except (SyntaxError, ValueError):
                    continue
                for node in ast.walk(tree):
                    if _is_strategy(node):
                        found.append((path, node.name))
        for path, strategy in sorted(found, key=lambda x: (x[0], x[1])):
            if strategy in seen:
                continue
            seen.add(strategy)
            rows.append({"repo": repo, "path": path, "strategy": strategy})
    return rows


def strategy_node(path, strategy, source=None):
    """Parse only the selected implementation; do not retain corpus-wide ASTs."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        tree = ast.parse(source if source is not None else _read(path), filename=path)
    for node in ast.walk(tree):
        if _is_strategy(node) and node.name == strategy:
            return node
    raise ValueError("strategy class not found: %s in %s" % (strategy, path))


def _constant_bool(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, bool):
        return node.value
    if hasattr(ast, "NameConstant") and isinstance(node, ast.NameConstant):
        return node.value if isinstance(node.value, bool) else None
    return None


def declared_can_short(class_node):
    values = []
    for statement in class_node.body:
        if isinstance(statement, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == "can_short" for t in statement.targets):
                values.append(_constant_bool(statement.value))
        elif isinstance(statement, ast.AnnAssign):
            if isinstance(statement.target, ast.Name) and statement.target.id == "can_short":
                values.append(_constant_bool(statement.value))
    if not values:
        return "absent"
    value = values[-1]
    return "true" if value is True else "false" if value is False else "dynamic"


def declared_text(class_node, attribute):
    for statement in reversed(class_node.body):
        value = None
        if isinstance(statement, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == attribute for t in statement.targets
        ):
            value = statement.value
        elif isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name) \
                and statement.target.id == attribute:
            value = statement.value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            return value.value
    return ""


def _target_strings(target):
    return {
        node.value
        for node in ast.walk(target)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }


def entry_writes(class_node):
    """Find explicit writes to Freqtrade entry columns inside the class."""
    writes = set()
    methods = set()
    for node in ast.walk(class_node):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            methods.add(node.name)
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                writes.update(_target_strings(target))
    long_entry = bool(writes.intersection(("enter_long", "buy")))
    short_entry = "enter_short" in writes
    # Some old strategies return a signal series without a literal assignment.
    # A legacy buy method is still positive long-entry evidence, while a generic
    # entry method without a recognized column stays unknown.
    if "populate_buy_trend" in methods:
        long_entry = True
    return long_entry, short_entry, methods, writes


def _profile(path, class_node, can_short, long_entry, short_entry, methods):
    rel_lower = path.replace("\\", "/").lower()
    futures_path = any(token in rel_lower for token in ("/futures/", "_futures", "futures "))
    short_path = any(token in rel_lower for token in ("_short", "/short", "short."))
    method_names = set(methods)
    hard_futures = can_short == "true" or "leverage" in method_names
    metadata_futures = futures_path or short_path

    if long_entry and short_entry:
        signal_capability = "long_short"
    elif short_entry:
        signal_capability = "short_only"
    elif long_entry:
        signal_capability = "long_only"
    else:
        signal_capability = "unknown"

    # Native direction includes Freqtrade's can_short gate.  A dormant
    # enter_short column is still recorded above, but it does not turn the
    # published strategy into an executable short strategy.
    if can_short == "true":
        direction = signal_capability
    elif long_entry:
        direction = "long_only"
    else:
        direction = "unknown"

    intent = "futures" if hard_futures or metadata_futures or short_entry else "unspecified"
    if hard_futures:
        mode = "futures"
    elif metadata_futures:
        mode = "futures"
    else:
        mode = "spot"

    if mode == "spot":
        run_profile = "spot_long" if direction in ("long_only", "unknown") else "unknown"
    elif direction == "long_short":
        run_profile = "futures_long_short"
    elif direction == "short_only":
        run_profile = "futures_short"
    elif direction == "long_only":
        run_profile = "futures_long"
    else:
        run_profile = "unknown"

    reasons = []
    review = False
    if can_short == "true" and not short_entry:
        review = True
        reasons.append("can_short=true but no explicit enter_short write")
    if short_entry and can_short != "true":
        review = True
        reasons.append("enter_short is dormant without a literal can_short=true")
    if signal_capability == "unknown":
        review = True
        reasons.append("no explicit long or short entry write")
    if metadata_futures and not hard_futures:
        review = True
        reasons.append("futures intent inferred only from path/name")
    if not reasons:
        reasons.append("mode and direction agree with static source evidence")
    evidence = "static_code" if (long_entry or short_entry or hard_futures) else "metadata"
    return {
        "signal_capability": signal_capability,
        "direction_capability": direction,
        "author_mode_intent": intent,
        "mode_support": mode,
        "run_profile": run_profile,
        "evidence_level": evidence,
        "classification_status": "review" if review else "provisional",
        "classification_reason": "; ".join(reasons),
    }


def _load_cards(directory):
    cards = {}
    if not os.path.isdir(directory):
        return cards
    for filename in sorted(os.listdir(directory)):
        if not filename.endswith(".json"):
            continue
        try:
            card = json.load(io.open(os.path.join(directory, filename), encoding="utf-8"))
        except (ValueError, OSError):
            continue
        strategy = card.get("strategy")
        if strategy:
            cards[strategy] = card
    return cards


def _measured(card):
    if not card:
        return False
    summary = ((card.get("runs") or {}).get("in_sample") or {}).get("summary")
    return isinstance(summary, dict) and summary.get("trades") is not None


def _card_trades(card):
    total = 0
    found = False
    for name in ("in_sample", "out_sample"):
        summary = (((card or {}).get("runs") or {}).get(name) or {}).get("summary")
        if isinstance(summary, dict) and summary.get("trades") is not None:
            total += int(summary["trades"])
            found = True
    return total if found else None


def _number(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _load_patch_report(repair_root):
    path = os.path.join(repair_root, "patch_class2_report.json")
    if not os.path.exists(path):
        return {}
    rows = json.load(io.open(path, encoding="utf-8"))
    return {row["strategy"]: row for row in rows if row.get("action") == "patched"}


def _ledger_rows():
    path = os.path.join(ROOT, "LEDGER.csv")
    if not os.path.exists(path):
        return {}
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return {row["strategy"]: row for row in csv.DictReader(handle)}


def _smoke_results():
    path = os.path.join(ROOT, "PROFILE_SMOKE.json")
    if not os.path.exists(path):
        return {}
    try:
        data = json.load(io.open(path, encoding="utf-8"))
    except (ValueError, OSError):
        return {}
    return data.get("results") or {}


def _profile_repairs():
    path = os.path.join(ROOT, "PROFILE_REPAIRS.json")
    if not os.path.exists(path):
        return {}
    try:
        data = json.load(io.open(path, encoding="utf-8"))
    except (ValueError, OSError):
        return {}
    return {row["strategy"]: row for row in data.get("repairs", [])}


def _profile_class1():
    path = os.path.join(ROOT, "PROFILE_CLASS1.json")
    if not os.path.exists(path):
        return {}
    try:
        data = json.load(io.open(path, encoding="utf-8"))
    except (ValueError, OSError):
        return {}
    return data.get("strategies") or {}


def _rel(path, base=ROOT):
    return os.path.relpath(path, base).replace(os.sep, "/")


def _config_timeframe(environment):
    source = environment.get("config_source")
    if not source or "timeframe" not in (environment.get("config_keys") or []):
        return ""
    path = os.path.join(ROOT, source.replace("/", os.sep))
    try:
        data = json.load(io.open(path, encoding="utf-8-sig"))
    except ValueError:
        # Some author configs are JSONC. Reuse the same quote-aware parser as
        # the runtime smoke harness rather than deleting // inside URLs.
        try:
            from profile_smoke import _read_jsonc
            data = _read_jsonc(path)
        except (ValueError, OSError):
            return ""
    except OSError:
        return ""
    value = data.get("timeframe")
    return value if isinstance(value, str) else ""


def build(repair_root=DEFAULT_REPAIR):
    original_cards = _load_cards(os.path.join(ROOT, "results"))
    class1_cards = _load_cards(os.path.join(repair_root, "results_class1"))
    freqai_cards = _load_cards(os.path.join(repair_root, "results_freqai"))
    patches = _load_patch_report(repair_root)
    ledger = _ledger_rows()
    smoke_results = _smoke_results()
    profile_repairs = _profile_repairs()
    profile_class1 = _profile_class1()
    rows = []

    for item in discover():
        strategy = item["strategy"]
        original_path = item["path"]
        source = _read(original_path)
        node = strategy_node(original_path, strategy, source)
        can_short = declared_can_short(node)
        timeframe = declared_text(node, "timeframe")
        environment = profile_class1.get(strategy) or {}
        config_timeframe = _config_timeframe(environment)
        execution_timeframe = timeframe or config_timeframe
        timeframe_source = ("strategy_source" if timeframe else
                            "author_config" if config_timeframe else "unresolved")
        long_entry, short_entry, methods, _writes = entry_writes(node)
        profile = _profile(original_path, node, can_short, long_entry, short_entry, methods)
        rel_lower = _rel(original_path).lower()
        artifact_role = (
            "test_candidate" if "/tests/" in ("/" + rel_lower)
            else "template_candidate" if profile["signal_capability"] == "unknown"
            else "strategy"
        )
        ledger_row = ledger.get(strategy) or {}
        historical_full = bool(ledger_row.get("is_trades") != "" and
                               ledger_row.get("os_trades") != "")
        original_ok = _measured(original_cards.get(strategy)) or historical_full
        class1_ok = _measured(class1_cards.get(strategy))
        freqai_ok = _measured(freqai_cards.get(strategy))
        original_trades = (_number(ledger_row.get("is_trades")) +
                           _number(ledger_row.get("os_trades"))
                           if historical_full else _card_trades(original_cards.get(strategy)))
        class1_trades = _card_trades(class1_cards.get(strategy))
        freqai_trades = _card_trades(freqai_cards.get(strategy))
        patch = patches.get(strategy)

        canonical_path = original_path
        population = "original"
        repair_class = ""
        repair_rules = ""
        equivalence = "not_applicable"
        source_tree = "original"
        canonical_ok = original_ok
        canonical_trades = original_trades
        trade_source = "historical_ledger" if historical_full else (
            "original_result_card" if original_trades is not None else "")

        # Prefer a working original.  Otherwise select the strongest documented
        # repair available; the original result remains available for the paired
        # repair-sensitivity table but is not a second canonical row.
        if not original_ok and patch:
            candidate = os.path.join(repair_root, "patched", patch["file"].replace("/", os.sep))
            if os.path.exists(candidate):
                canonical_path = candidate
                population = "repaired"
                repair_class = patch.get("repair_class", "class2")
                repair_rules = ";".join(patch.get("repair_rules") or patch.get("rule") or [])
                equivalence = patch.get("equivalence_status", "not_assessed")
                source_tree = patch.get("source_tree", "class2-overlay")
                canonical_ok = class1_ok or freqai_ok
                canonical_trades = class1_trades if class1_ok else freqai_trades
                trade_source = "class1_result_card" if class1_ok else "freqai_result_card"
        elif not original_ok and class1_ok:
            population = "repaired"
            repair_class = "class1"
            repair_rules = "environment_compatibility"
            equivalence = "strict_equivalent"
            source_tree = "original+compatibility-environment"
            canonical_ok = True
            canonical_trades = class1_trades
            trade_source = "class1_result_card"
        elif not original_ok and freqai_ok:
            population = "repaired"
            repair_class = "freqai_runtime"
            repair_rules = "freqai_training_configuration"
            equivalence = "not_assessed"
            source_tree = "original+freqai-runtime"
            canonical_ok = True
            canonical_trades = freqai_trades
            trade_source = "freqai_result_card"

        profile_repair = profile_repairs.get(strategy)
        if profile_repair:
            expected = profile_repair.get("input_sha256")
            # PROFILE_REPAIRS hashes normalized UTF-8 text so CRLF/LF checkout
            # differences do not invalidate an otherwise identical source.
            actual = "sha256_" + hashlib.sha256(
                _read(canonical_path).encode("utf-8")).hexdigest()
            candidate = os.path.join(ROOT, profile_repair["overlay_file"].replace("/", os.sep))
            if expected == actual and os.path.exists(candidate):
                canonical_path = candidate
                population = "repaired"
                repair_class = "class2"
                stacked_rules = [rule for rule in repair_rules.split(";") if rule]
                stacked_rules.extend(profile_repair.get("repair_rules") or [])
                repair_rules = ";".join(stacked_rules)
                if profile_repair.get("equivalence_status") == "output_equivalent" \
                        or equivalence == "output_equivalent":
                    equivalence = "output_equivalent"
                else:
                    equivalence = profile_repair.get("equivalence_status", "not_assessed")
                source_tree = profile_repair.get("source_tree", "profile-class2-overlay")

        # A successful historical result validates only the old spot mode.  It
        # does not validate the inferred direction or futures compatibility.
        validated_modes = ["spot"] if (
            original_ok or (canonical_ok and profile["run_profile"] == "spot_long")) else []
        if original_ok:
            if profile["mode_support"] == "futures":
                profile["mode_support"] = "both"
                profile["classification_status"] = "review"
                profile["classification_reason"] += "; historical spot run succeeded despite futures intent"
            profile["evidence_level"] = "runtime_full"

        smoke = smoke_results.get(strategy) or {}
        if smoke.get("status") == "measured":
            if smoke.get("mode") and smoke["mode"] not in validated_modes:
                validated_modes.append(smoke["mode"])
            canonical_ok = True
            if profile["evidence_level"] != "runtime_full":
                profile["evidence_level"] = "runtime_smoke"
            if profile["classification_status"] == "provisional":
                profile["classification_status"] = "validated"
            canonical_trades = _number(smoke.get("long_trades")) + _number(smoke.get("short_trades"))
            trade_source = "runtime_smoke"

        digest = hashlib.sha256(io.open(canonical_path, "rb").read()).hexdigest()
        row = {
            "strategy_id": strategy,
            "implementation_id": "%s:%s" % (strategy, digest[:12]),
            "strategy": strategy,
            "repo": item["repo"],
            "original_file": _rel(original_path),
            "canonical_file": _rel(canonical_path),
            "canonical_population": population,
            "repair_class": repair_class,
            "repair_rules": repair_rules,
            "environment_repair_status": environment.get("status", ""),
            "environment_repair_rules": ";".join(environment.get("rules") or []),
            "equivalence_status": equivalence,
            "source_tree": source_tree,
            "variant": "native",
            "ledger_present": str(strategy in ledger).lower(),
            "original_measured_spot": str(original_ok).lower(),
            "historical_is_trades": ledger_row.get("is_trades", ""),
            "historical_os_trades": ledger_row.get("os_trades", ""),
            "historical_full_measured": str(historical_full).lower(),
            "canonical_measured": str(canonical_ok).lower(),
            "declared_timeframe": timeframe,
            "execution_timeframe": execution_timeframe,
            "timeframe_source": timeframe_source,
            "declared_can_short": can_short,
            "static_long_entry": str(long_entry).lower(),
            "static_short_entry": str(short_entry).lower(),
            "has_leverage_callback": str("leverage" in methods).lower(),
            "artifact_role": artifact_role,
            "validated_modes": ";".join(validated_modes),
            "runtime_smoke_status": smoke.get("status", "not_run"),
            "runtime_smoke_timerange": smoke.get("timerange", ""),
            "observed_long_trades": smoke.get("long_trades", ""),
            "observed_short_trades": smoke.get("short_trades", ""),
            "canonical_observed_trades": "" if canonical_trades is None else canonical_trades,
            "trade_evidence_source": trade_source,
            "runtime_config_sha256": smoke.get("runtime_config_sha256", ""),
            "source_sha256": "sha256_" + digest,
        }
        row.update(profile)
        rows.append(row)
    return rows


def write_csv(rows, path):
    tmp = path + ".tmp"
    with io.open(tmp, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(tmp, path)


def selftest():
    source = """
class Both(IStrategy):
    can_short = True
    def populate_entry_trend(self, dataframe, metadata):
        dataframe.loc[dataframe.x > 0, 'enter_long'] = 1
        dataframe.loc[dataframe.x < 0, ['enter_short', 'enter_tag']] = (1, 's')
        return dataframe
"""
    node = ast.parse(source).body[0]
    assert declared_can_short(node) == "true"
    long_entry, short_entry, methods, _ = entry_writes(node)
    assert long_entry and short_entry
    profile = _profile("x.py", node, "true", long_entry, short_entry, methods)
    assert profile["run_profile"] == "futures_long_short"

    profile = _profile("x.py", node, "false", long_entry, short_entry, methods)
    assert profile["signal_capability"] == "long_short"
    assert profile["direction_capability"] == "long_only"
    assert profile["run_profile"] == "spot_long"

    source = """
class OldLong(IStrategy):
    def populate_buy_trend(self, dataframe, metadata):
        return dataframe
"""
    node = ast.parse(source).body[0]
    long_entry, short_entry, methods, _ = entry_writes(node)
    assert long_entry and not short_entry
    assert _profile("x.py", node, "absent", long_entry, short_entry, methods)["run_profile"] == "spot_long"
    print("execution_profiles selftest: PASS")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--repair-root", default=DEFAULT_REPAIR)
    parser.add_argument("--output", default=os.path.join(ROOT, "EXECUTION_PROFILES.csv"))
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    rows = build(os.path.abspath(args.repair_root))
    write_csv(rows, os.path.abspath(args.output))
    counts = {}
    for row in rows:
        key = row["run_profile"]
        counts[key] = counts.get(key, 0) + 1
    print("canonical strategies: %d" % len(rows))
    for key in sorted(counts):
        print("  %-20s %d" % (key, counts[key]))
    print("review required: %d" % sum(r["classification_status"] == "review" for r in rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
