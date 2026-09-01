# -*- coding: utf-8 -*-
"""Put the author's own helper module back on the import path.

Seventeen rows fail to load because they import a module that is not installed
anywhere - `custom_indicators`, `alpha`, `utils`, `remora`. The module is not
missing: it is in the corpus, in the repository the strategy came from or in
the repository the strategy was copied out of. Nothing about the strategy is
wrong. Our import path does not reach the file the author imported.

WHICH COPY. Several repositories carry a `custom_indicators.py`, and they are
not the same file. Picking one by name would be a guess with a plausible shape,
and a wrong helper does not fail loudly - it computes different indicators
under the same names. So a candidate is accepted only on evidence: its
directory is put on the path and the strategy file is imported. A candidate
that does not make the import succeed is not the module the author meant. When
several do, they are compared byte for byte, and a real disagreement is
reported rather than resolved by preference.

That test also catches the name collisions this search invites. `BinanceStream`
imports `binance`, the PyPI package; the corpus happens to contain a directory
of that name belonging to somebody else. It does not satisfy the import, so it
is not offered.

WHAT THIS IS AND IS NOT. Adding a directory to `PYTHONPATH` restores what the
author had when they wrote the file. No strategy source is touched and no
behaviour is supplied. The result is recorded in `PROFILE_CLASS1.json` under
the rule that already exists for it, `restore_copied_local_module`, with the
evidence that chose the copy.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import io
import json
import os
import re
import sys
import traceback


ROOT = os.path.dirname(os.path.abspath(__file__))
TRIAGE = os.path.join(ROOT, "BLOCKED_TRIAGE.json")
CLASS1 = os.path.join(ROOT, "PROFILE_CLASS1.json")
OUTPUT = os.path.join(ROOT, "REPAIR_LOCAL_MODULES.json")
RULE = "restore_copied_local_module"


def _json(path):
    return json.load(io.open(path, encoding="utf-8"))


def _write(path, data):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)


_WALK = None


def _corpus():
    """The corpus walked once. Seventeen full walks was most of the runtime."""
    global _WALK
    if _WALK is None:
        _WALK = [(base, set(dirs), set(files))
                 for base, dirs, files in os.walk(os.path.join(ROOT, "repos"))]
    return _WALK


def candidates(module):
    """Every copy of `module` in the corpus, as directories to put on the path."""
    top = module.split(".")[0]
    found = []
    for base, dirs, files in _corpus():
        if top + ".py" in files:
            found.append((base, os.path.join(base, top + ".py")))
        if top in dirs and os.path.exists(
                os.path.join(base, top, "__init__.py")):
            found.append((base, os.path.join(base, top, "__init__.py")))
    return found


def registered_paths():
    """Paths this audit has already chosen for the same rule, elsewhere.

    A choice already on the record is not a new judgement. `DWT_LongShort`,
    `DWT_short` and `FTT_DWT_FBB_FUTURES` were given werkkrew's solipsis
    directory when they were repaired; `DWT` and the Solipsis rows are the same
    lineage and the same helper. Following that is consistency, and departing
    from it would need a reason.
    """
    if not os.path.exists(CLASS1):
        return []
    out = []
    for entry in _json(CLASS1).get("strategies", {}).values():
        if RULE in (entry.get("rules") or []):
            out.extend(entry.get("python_paths") or [])
    return out


# A directory that also contains one of these shadows the real package the
# moment it goes on sys.path, and the failure it causes looks nothing like its
# cause: `cannot import name '__version__' from 'freqtrade' (unknown
# location)`. Four rows were repaired into exactly that before this existed.
SHADOWS = ("freqtrade", "numpy", "pandas", "talib", "technical", "scipy",
           "sklearn", "ccxt", "arrow", "rich")


def shadows_a_package(directory):
    """The installed package this directory would hide, or ""."""
    for name in SHADOWS:
        if os.path.isdir(os.path.join(directory, name))                 or os.path.isfile(os.path.join(directory, name + ".py")):
            return name
    return ""


def _digest(path):
    return hashlib.sha256(io.open(path, "rb").read()).hexdigest()[:16]


def try_import(source_file, extra_path):
    """Import the strategy with `extra_path` on sys.path. Returns "" or why not."""
    path = os.path.join(ROOT, source_file.replace("/", os.sep))
    name = "probe_%s" % re.sub(r"\W+", "_", os.path.basename(path))
    sys.path.insert(0, extra_path)
    previous = sys.modules.pop(name, None)
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            return "no loader"
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        try:
            spec.loader.exec_module(module)
        except BaseException as exc:        # noqa: BLE001 - the answer we want
            return "%s: %s" % (type(exc).__name__, str(exc)[:120])
        return ""
    finally:
        sys.modules.pop(name, None)
        if previous is not None:
            sys.modules[name] = previous
        try:
            sys.path.remove(extra_path)
        except ValueError:
            pass


def resolve(record):
    """Which copy of the missing module makes this strategy import, and why."""
    module = record["missing_module"]
    strategy = record["strategy_id"]
    source = record["source_file"].replace(os.sep, "/")
    repo = "/".join(source.split("/")[:2])
    result = {"strategy_id": strategy, "missing_module": module,
              "source_file": source, "rule": RULE}
    tried = []
    working = []
    for directory, file_path in candidates(module):
        relative = os.path.relpath(directory, ROOT).replace(os.sep, "/")
        shadowed = shadows_a_package(directory)
        if shadowed:
            tried.append({"path": relative, "imports": False,
                          "sha256_16": _digest(file_path),
                          "why": ("would shadow the installed %s package"
                                  % shadowed)})
            continue
        why = try_import(source, directory)
        tried.append({"path": relative, "imports": not why,
                      "sha256_16": _digest(file_path), "why": why})
        if not why:
            working.append((relative, _digest(file_path)))
    result["candidates"] = tried
    if not working:
        result["status"] = "unresolved"
        result["why"] = ("no copy of %s in the corpus makes %s import; the "
                         "import failure is not only this module"
                         % (module, strategy))
        return result
    digests = {digest for _path, digest in working}
    same_repo = [path for path, _d in working if path.startswith(repo + "/")
                 or path == repo]
    known = [path for path, _d in working if path in registered_paths()]
    result["copies_that_work"] = [path for path, _d in working]
    result["status"] = "resolved"
    if len(digests) == 1:
        result["python_path"] = same_repo[0] if same_repo else working[0][0]
        result["why"] = ("%d copies satisfy the import and all are the same "
                         "file, so the choice carries no risk" % len(working))
    elif same_repo:
        result["python_path"] = same_repo[0]
        result["why"] = ("%d differing copies satisfy the import; the one in "
                         "the strategy's own repository is used"
                         % len(working))
    elif known:
        result["python_path"] = known[0]
        result["why"] = ("%d differing copies satisfy the import and none is "
                         "in the strategy's own repository; %s is the one this "
                         "audit already chose for the same helper elsewhere, "
                         "so following it is consistency rather than a new "
                         "judgement" % (len(working), known[0]))
    else:
        result["status"] = "ambiguous"
        result["why"] = ("%d differing copies satisfy the import, none is in "
                         "the strategy's own repository and none has been "
                         "chosen before, so which helper the author meant is "
                         "not established here" % len(working))
    return result


def run(write_class1):
    triage = _json(TRIAGE)["results"]
    rows = [r for r in triage.values()
            if r.get("family") == "local_module_off_path"]
    results = {}
    for record in sorted(rows, key=lambda r: r["strategy_id"]):
        resolved = resolve(record)
        results[record["strategy_id"]] = resolved
        print("%-34s %-22s %s" % (record["strategy_id"], resolved["status"],
                                  resolved.get("python_path")
                                  or resolved["why"][:70]), flush=True)
    _write(OUTPUT, {"schema_version": 1, "rule": RULE, "results": results})
    counts = collections.Counter(r["status"] for r in results.values())
    print()
    for key, count in counts.most_common():
        print("   %-12s %d" % (key, count))
    if write_class1:
        applied = apply_to_class1(results)
        print("wrote %d entries to PROFILE_CLASS1.json" % applied)
    return 0


def apply_to_class1(results):
    """Register the resolved paths where the runners already look for them."""
    data = _json(CLASS1)
    strategies = data.setdefault("strategies", {})
    applied = 0
    for strategy, record in sorted(results.items()):
        if record["status"] != "resolved":
            continue
        entry = strategies.setdefault(strategy, {})
        rules = list(entry.get("rules", []))
        if RULE not in rules:
            rules.append(RULE)
        paths = list(entry.get("python_paths", []))
        if record["python_path"] not in paths:
            paths.append(record["python_path"])
        entry.update({"rules": rules, "python_paths": paths,
                      "status": "applied",
                      "note": record["why"]})
        applied += 1
    _write(CLASS1, data)
    return applied


MEASURED = os.path.join(ROOT, "ELIGIBILITY_MODULE_REPAIR.json")


def verify():
    """What the repaired rows actually did when they were run.

    A path that satisfies the import is not yet a repair. `Solipsis6` imports
    with werkkrew's `custom_indicators` and then asks it for `bollinger_bands`,
    which that copy does not define - and no copy in the corpus does. The
    import test cannot see that, and only the run can, so the run's verdict is
    written back beside the resolution.
    """
    if not os.path.exists(MEASURED):
        print("no measurements yet: %s" % os.path.basename(MEASURED))
        return 0
    measured = _json(MEASURED).get("results", {})
    data = _json(OUTPUT)
    for strategy, record in data["results"].items():
        run = measured.get(strategy)
        if not run:
            continue
        why = (run.get("why") or "")
        record["verified_status"] = run.get("status")
        record["verified_why"] = why[:200]
        if run.get("status") == "measured":
            record["verification"] = "repaired"
        elif record["missing_module"].split(".")[0] in why:
            # Still about the same module: the copy is on the path but is not
            # the one the author had.
            record["verification"] = "path_insufficient"
        else:
            # Past the module and failing on something else. The repair did
            # its job; what remains is a different question.
            record["verification"] = "past_the_module"
    _write(OUTPUT, data)
    counts = collections.Counter(r.get("verification", "not_run")
                                 for r in data["results"].values())
    for key, count in counts.most_common():
        print("   %-20s %d" % (key, count))
    return 0


def selftest():
    triage = _json(TRIAGE)["results"]
    rows = [r for r in triage.values()
            if r.get("family") == "local_module_off_path"]
    assert rows, "no local-module rows in the triage"
    for record in rows:
        assert record.get("missing_module"), record["strategy_id"]
        assert record.get("source_file"), record["strategy_id"]
    if os.path.exists(OUTPUT):
        results = _json(OUTPUT)["results"]
        for strategy, record in results.items():
            # A path may only be registered on the evidence that it works.
            if record["status"] == "resolved":
                assert record.get("python_path"), strategy
                assert record["python_path"] in record["copies_that_work"], \
                    strategy
            else:
                assert "python_path" not in record, strategy
        # Nothing registered in the runner's config without a resolved record.
        class1 = _json(CLASS1).get("strategies", {})
        for strategy, entry in class1.items():
            if RULE in entry.get("rules", []) and strategy in results:
                assert results[strategy]["status"] == "resolved", strategy
    print("repair_local_modules selftest: PASS (%d rows)" % len(rows))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="write the resolved paths into PROFILE_CLASS1.json")
    parser.add_argument("--verify", action="store_true",
                        help="write back what the repaired rows did when run")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.verify:
        return verify()
    if args.selftest:
        selftest()
        return 0
    return run(args.apply)


if __name__ == "__main__":
    sys.exit(main())
