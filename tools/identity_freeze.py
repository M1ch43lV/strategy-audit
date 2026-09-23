# -*- coding: utf-8 -*-
"""Fail the build when an identity input changes silently.

WHY THIS IS A GUARD AND NOT A COMMENT. Whether stored evidence is re-measured
is decided by one comparison, repeated in several places:

    all(previous.get(key) == value for key, value in identity.items())

The stored record must match EVERY key of the identity mapping. That makes the
key sets load-bearing in a way that is easy to break by accident: adding one
field - say `verdict_schema_version` - to `profile_smoke._identity()` makes
every stored smoke record non-current, and the next run re-measures the whole
corpus instead of reading it. `regime/full_backtest.py` records that this has
already happened once:

    Folding the broader fingerprint below into this check too would read every
    one of the hundreds of already-measured rows as stale the moment this field
    first existed, since none of them carry it yet.

So the key sets are frozen here, the policy tokens that are hashed into records
are frozen here, and the parameters hash of `evidence/execution_robustness.py`
is recomputed here from the module's own literals. A deliberate change is
allowed - it just has to be made here too, where it is visible in a diff and
where the cost of re-measurement is stated next to it.

WHAT THIS FILE DELIBERATELY DOES NOT DO. It does not import the frozen modules.
`evidence/profile_smoke.py` and `evidence/profile_bias.py` need a real profile
row and real strategy files to call their identity functions, which a CI
checkout does not have. The key sets are read from the AST instead, which is
exact for these functions and needs no data. `--selftest` proves the extractor
still finds what it claims, by planting a change and requiring the check to
catch it.

    python tools/identity_freeze.py             # the guard
    python tools/identity_freeze.py --selftest  # prove the guard bites
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import io
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# ── the frozen identity inputs ──────────────────────────────────────────────
# cost of a change: every stored record of that store becomes non-current and is
# re-measured on the next run. Smoke, bias and the canonical full backtest all
# read these two functions, so an added key there is a corpus-wide rerun.
FROZEN_IDENTITY = (
    ("evidence/profile_smoke.py", "_identity",
     frozenset(("canonical_sha256", "runtime_config_sha256"))),
    ("evidence/profile_bias.py", "identity",
     frozenset(("canonical_sha256", "runtime_config_sha256",
                "mode", "run_profile", "class1_rules"))),
    ("evidence/eligibility_warmup.py", "identity",
     frozenset(("implementation_id", "canonical_sha256",
                "runtime_config_sha256", "run_profile", "mode",
                "class1_rules", "diagnostic_rule", "startup_candle_count"))),
    # Wraps profile_smoke._identity and adds two fields of its own; the base keys
    # are inherited, so only the added ones are listed here.
    ("repair/timeframe_5m_recovery.py", "_identity",
     frozenset(("source_execution_timeframe", "recovery_execution_timeframe"))),
)

# name -> (module path, expected literal). These strings are hashed into every
# record they appear in, so renaming one invalidates that store's evidence.
FROZEN_POLICY_TOKENS = (
    ("SMOKE_POLICY_ID", "evidence/profile_smoke.py",
     "fixed_1m_3m_until_10_trades_v2"),
    ("RULE", "evidence/eligibility_warmup.py", "diagnostic_startup_override_v1"),
)

# The parameters hash of the detail classifier and cost screen, rebuilt here
# from THRESHOLDS, COST and DETAIL_RULE in that module's own source. Renaming a
# threshold or moving the detail rule changes the records of every robustness
# measurement.
FROZEN_ROBUSTNESS_PARAMETERS = (
    "sha256_08e3ff0a1ac8bb7b0720f7adbd47ec32a87a38e3f77a98457804374b9e0a2d61"
)
ROBUSTNESS_MODULE = "evidence/execution_robustness.py"
ROBUSTNESS_LITERALS = ("THRESHOLDS", "COST", "DETAIL_RULE")

POLICY_JSON = Path("evidence/REGIME_COVERAGE_POLICY.json")
FROZEN_COVERAGE_POLICY_VERSION = "1"


def _tree(relative):
    path = ROOT / relative
    return ast.parse(io.open(path, encoding="utf-8").read()), path


def _find_function(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _identity_keys(function):
    """String keys a function puts into the mapping it returns.

    Covers the three shapes the audit actually uses: a returned dict literal, a
    `for field, path in (...)` loop that fills the dict, and `value["k"] = ...`
    assignments onto an inherited mapping.
    """
    keys = set()
    for node in ast.walk(function):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
            for key in node.value.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    keys.add(key.value)
        if (isinstance(node, ast.For) and isinstance(node.target, ast.Tuple)
                and isinstance(node.iter, ast.Tuple)):
            first = node.target.elts[0] if node.target.elts else None
            if isinstance(first, ast.Name):
                for element in node.iter.elts:
                    if not (isinstance(element, ast.Tuple) and element.elts):
                        continue
                    head = element.elts[0]
                    if isinstance(head, ast.Constant) and isinstance(head.value, str):
                        keys.add(head.value)
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if (isinstance(target, ast.Subscript)
                        and isinstance(target.value, ast.Name)
                        and isinstance(target.slice, ast.Constant)
                        and isinstance(target.slice.value, str)):
                    keys.add(target.slice.value)
    return keys


def _module_constant(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
    return None


def _module_imports(tree):
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def _verdict_tokens():
    """The verdict vocabulary, loaded without putting the repo on sys.path."""
    path = ROOT / "evidence" / "verdicts.py"
    spec = importlib.util.spec_from_file_location("_audit_verdicts", path)
    module = importlib.util.module_from_spec(spec)
    # The `dataclass` decorator resolves the defining module through sys.modules
    # while it runs, so the module must be registered before exec_module.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.tokens()


def _identity_verdict_literals(function, vocabulary):
    """Verdict tokens found inside an identity function - never allowed."""
    found = set()
    for node in ast.walk(function):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in vocabulary:
                found.add(node.value)
    return found


def _robustness_digest(tree=None):
    """The parameters hash, rebuilt from the module's literals."""
    tree = tree or _tree(ROBUSTNESS_MODULE)[0]
    literals = {name: _module_constant(tree, name)
                for name in ROBUSTNESS_LITERALS}
    if any(value is None for value in literals.values()):
        return None, literals
    parameters = {"thresholds": literals["THRESHOLDS"],
                  "cost": literals["COST"],
                  "detail_rule": literals["DETAIL_RULE"]}
    text = json.dumps(parameters, sort_keys=True, separators=(",", ":"))
    return "sha256_" + hashlib.sha256(text.encode("utf-8")).hexdigest(), literals


def compare_keys(module, function_name, frozen, actual):
    """Return the problem lines for one identity function. Shared with the
    selftest, so the guard and its proof cannot drift apart."""
    problems = []
    added = sorted(actual - frozen)
    removed = sorted(frozen - actual)
    label = "%s::%s" % (module, function_name)
    if added:
        problems.append(
            "%s: ADDED %s - every stored record of this store becomes "
            "non-current and is re-measured. If that is intended, add the key "
            "here in the same commit and say what it costs." % (label, added))
    if removed:
        problems.append(
            "%s: REMOVED %s - stored records no longer agree on what was "
            "measured." % (label, removed))
    if not actual:
        problems.append(
            "%s: extracted no keys at all. The extractor no longer understands "
            "this function; fix the extractor before trusting a green run."
            % label)
    return problems


def run(verbose=True):
    """Return the list of problems. Empty means every frozen input held."""
    problems = []
    vocabulary = _verdict_tokens()

    for module, function_name, frozen in FROZEN_IDENTITY:
        tree, _path = _tree(module)
        function = _find_function(tree, function_name)
        if function is None:
            problems.append("%s::%s: function not found" % (module, function_name))
            continue
        actual = _identity_keys(function)
        problems.extend(compare_keys(module, function_name, frozen, actual))
        planted = _identity_verdict_literals(function, vocabulary)
        if planted:
            problems.append(
                "%s::%s: contains verdict tokens %s. Identity inputs decide "
                "whether evidence is re-measured; a status word must never "
                "enter one." % (module, function_name, sorted(planted)))
        if "verdicts" in _module_imports(tree):
            problems.append(
                "%s: imports the verdict schema. The schema is a read-side "
                "layer and must stay out of any hashed input." % module)
        if verbose:
            print("  identity %-45s %d key(s) frozen"
                  % ("%s::%s" % (module, function_name), len(frozen)))

    for name, module, expected in FROZEN_POLICY_TOKENS:
        actual = _module_constant(_tree(module)[0], name)
        if actual != expected:
            problems.append(
                "%s.%s is %r, expected %r. This token is hashed into stored "
                "records; renaming it invalidates that store's evidence."
                % (module, name, actual, expected))
        elif verbose:
            print("  policy   %-45s %r" % ("%s.%s" % (module, name), actual))

    digest, literals = _robustness_digest()
    if digest is None:
        problems.append(
            "%s: could not read %s from the source; the extractor, not the "
            "thresholds, is what changed." % (ROBUSTNESS_MODULE,
                                              list(ROBUSTNESS_LITERALS)))
    elif digest != FROZEN_ROBUSTNESS_PARAMETERS:
        problems.append(
            "%s: parameters hash is %s, expected %s. A threshold or the detail "
            "rule moved, which invalidates every recorded robustness "
            "measurement." % (ROBUSTNESS_MODULE, digest,
                              FROZEN_ROBUSTNESS_PARAMETERS))
    elif verbose:
        print("  policy   %-45s %s" % (ROBUSTNESS_MODULE + "::parameters",
                                       digest[:23] + "..."))

    if POLICY_JSON.is_file():
        with io.open(ROOT / POLICY_JSON, encoding="utf-8") as handle:
            version = json.load(handle).get("policy_version")
        if version != FROZEN_COVERAGE_POLICY_VERSION:
            problems.append(
                "%s: policy_version is %r, expected %r. It is part of the "
                "coverage fingerprint." % (POLICY_JSON, version,
                                           FROZEN_COVERAGE_POLICY_VERSION))
        elif verbose:
            print("  policy   %-45s %r" % (str(POLICY_JSON) + "::policy_version",
                                           version))
    return problems


def selftest():
    """Prove the guard bites: plant a change, require the check to catch it."""
    problems = list(run(verbose=False))

    # A planted added key must be reported as an added key.
    module, function_name, frozen = FROZEN_IDENTITY[0]
    planted = frozenset(frozen | {"verdict_schema_version"})
    caught = compare_keys(module, function_name, frozen, planted)
    if not any("ADDED" in line and "verdict_schema_version" in line
               for line in caught):
        problems.append("selftest: an added identity key was not reported")

    # A planted removed key must be reported as removed.
    caught = compare_keys(module, function_name, frozen, frozenset(frozen - {"canonical_sha256"}))
    if not any("REMOVED" in line and "canonical_sha256" in line
               for line in caught):
        problems.append("selftest: a removed identity key was not reported")

    # A function the extractor cannot read must be a failure, not a pass.
    caught = compare_keys("x.py", "f", frozenset({"a"}), frozenset())
    if not any("extracted no keys" in line for line in caught):
        problems.append("selftest: an unreadable function passed")

    # The real repository source, against a mutated expectation. This is the
    # only check here that proves the extractor and the comparator together on
    # the function whose keys actually matter.
    tree, _path = _tree(module)
    real = _identity_keys(_find_function(tree, function_name))
    caught = compare_keys(module, function_name,
                          frozenset(real | {"verdict_schema_version"}), real)
    if not any("REMOVED" in line and "verdict_schema_version" in line
               for line in caught):
        problems.append("selftest: the real source was not compared")

    # A verdict token planted inside an identity function must be caught.
    source = ("def _identity(row):\n"
              "    return {'canonical_sha256': row['sha'], 'status': 'PASS'}\n")
    function = _find_function(ast.parse(source), "_identity")
    planted_tokens = _identity_verdict_literals(function, _verdict_tokens())
    if planted_tokens != {"PASS"}:
        problems.append("selftest: a verdict token in an identity function "
                        "was not detected (%r)" % (sorted(planted_tokens),))

    # The digest must equal what the real module computes. Recomputing it from
    # literals is only useful if it is the same number the records carry.
    digest, _literals = _robustness_digest()
    if digest != FROZEN_ROBUSTNESS_PARAMETERS:
        problems.append("selftest: the extracted parameters hash does not match "
                        "the frozen one")

    # The three extractor shapes must all be understood.
    shapes = ast.parse(
        "def f(row):\n"
        "    out = {}\n"
        "    for field, path in (('a', 1), ('b', 2)):\n"
        "        out[field] = path\n"
        "    out['c'] = 3\n"
        "    return out\n")
    if _identity_keys(_find_function(shapes, "f")) != {"a", "b", "c"}:
        problems.append("selftest: the extractor lost a key shape")

    for problem in problems:
        print("FAIL %s" % problem)
    print("identity freeze selftest: %d problem(s)" % len(problems))
    return 1 if problems else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true",
                        help="prove the guard catches a planted change")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.quiet:
        print("frozen identity inputs:")
    problems = run(verbose=not args.quiet)
    for problem in problems:
        print("FAIL %s" % problem)
    print("identity freeze: %d problem(s)" % len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
